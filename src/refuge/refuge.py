#!/usr/bin/env python3
"""Campaña de supervivencia en terminal para Alexandria OS."""

import json
import os
import random
import select
import shutil
import subprocess
import sys
import tempfile
import textwrap
import termios
import time
import tty
from contextlib import contextmanager
from pathlib import Path

DIALOG = shutil.which("dialog")
STATE_HOME = os.environ.get("XDG_STATE_HOME")
STATE_ROOT = Path(STATE_HOME) if STATE_HOME else Path.home() / ".local" / "state"
SAVE_FILE = STATE_ROOT / "alexandria-os" / "the-refuge.json"
SAVE_VERSION = 1
MINIGAME_COLOR_CODES = {
    "red": "91",
    "green": "92",
    "yellow": "93",
    "blue": "94",
    "magenta": "95",
    "cyan": "96",
    "white": "97",
    "dim": "2",
}
MINIGAME_COLOR_ENABLED = (
    sys.stdout.isatty()
    and "NO_COLOR" not in os.environ
    and os.environ.get("TERM") != "dumb"
)

RESOURCE_NAMES = {
    "food": "Comida",
    "water": "Agua",
    "medicine": "Medicinas",
    "materials": "Materiales",
}
STAT_NAMES = {
    "survivors": "Supervivientes",
    "morale": "Moral",
    "defense": "Defensas",
    "intel": "Inteligencia",
    "alliances": "Alianzas",
}
STAT_SHORT_NAMES = {
    "survivors": "Sup.",
    "morale": "Moral",
    "defense": "Def.",
    "intel": "Intel.",
    "alliances": "Al.",
}
STAT_LIMITS = {
    "survivors": (0, 12),
    "morale": (0, 10),
    "defense": (0, 6),
    "intel": (0, 6),
    "alliances": (0, 5),
}
RESOURCE_LIMITS = {
    "food": 20,
    "water": 20,
    "medicine": 10,
    "materials": 10,
}

PREPARATION_TURNS = 5
WAR_TURNS = 8
WAR_RATION_COST = 2
INCIDENT_CHANCE = 0.38
EARLY_CAMPAIGN_PHASES = ("council", "expedition", "crisis", "recovery", "refugees")

PHASES = {
    "council": (
        "CONSEJO DEL REFUGIO",
        "La comunidad se prepara para una campaña larga. Elegí una prioridad para empezar.",
    ),
    "expedition": (
        "EXPEDICIÓN",
        "El grupo sale a buscar recursos. Algunas rutas son más peligrosas que otras.",
    ),
    "crisis": (
        "CRISIS EN EL PERÍMETRO",
        "Una amenaza se acerca mientras la comunidad aún se organiza. Tu respuesta afectará la preparación.",
    ),
    "recovery": (
        "RECONSTRUCCIÓN",
        "Hay que reparar daños, atender heridos y recuperar la confianza antes de la ofensiva.",
    ),
    "refugees": (
        "NUEVOS REFUGIADOS",
        "Un grupo llega desde una comunidad cercana. Aceptarlo puede ayudar, pero también consume reservas.",
    ),
    "preparation": (
        "PREPARACIÓN DEL REFUGIO",
        "La ofensiva se acerca. Elegí cada día entre abastecerse, cuidar al grupo o fortalecer la defensa.",
    ),
    "war": (
        "GUERRA CONTRA LOS SALVADORES",
        "La ofensiva avanza por ocho turnos. Cada decisión afecta los recursos y la capacidad de resistir; el frente consume dos raciones de comida y agua por turno.",
    ),
    "final": (
        "CONFRONTACIÓN FINAL",
        "Rick queda frente a Negan. La decisión final depende de la preparación acumulada y abre un desenlace alternativo.",
    ),
}


def call_dialog(args):
    if not DIALOG:
        print("No se encontró dialog. Instalalo como root con: su -c 'apt install dialog'")
        raise SystemExit(1)
    return subprocess.run(
        [DIALOG, "--clear", "--stdout", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def dialog_width(requested, content=()):
    columns = shutil.get_terminal_size(fallback=(80, 24)).columns
    maximum = max(40, columns - 4)
    if requested > 0:
        return min(requested, maximum)
    lines = []
    for block in content:
        lines.extend(str(block).splitlines() or [""])
    needed = max((len(line) for line in lines), default=68) + 8
    return min(maximum, max(68, needed))


def message(title, text, height=12, width=76):
    call_dialog(["--title", title, "--msgbox", text, str(height), str(width)])


def confirm(title, text, height=9, width=68):
    width = dialog_width(width, [text])
    result = call_dialog(["--title", title, "--yesno", text, str(height), str(width)])
    return result.returncode == 0


def choose(title, prompt, choices, height=20, width=78, menu_height=10):
    if not choices:
        return None
    content = [prompt, *(f"{tag} {description}" for tag, description in choices)]
    width = dialog_width(width, content)
    args = ["--title", title, "--menu", prompt, str(height), str(width), str(menu_height)]
    for tag, description in choices:
        args.extend([tag, description])
    result = call_dialog(args)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def create_campaign():
    return {
        "version": SAVE_VERSION,
        "status": "active",
        "day": 1,
        "phase": "council",
        "preparation_turn": 1,
        "war_turn": 0,
        "survivors": 12,
        "morale": 5,
        "defense": 1,
        "intel": 0,
        "alliances": 0,
        "shortage_streak": 0,
        "resources": {
            "food": 9,
            "water": 9,
            "medicine": 3,
            "materials": 4,
        },
        "decisions": [],
        "ending": None,
    }


def save_campaign(state):
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = SAVE_FILE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(SAVE_FILE)


def load_campaign():
    if not SAVE_FILE.is_file():
        return None
    try:
        state = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        message(
            "ARCHIVO DE CAMPAÑA",
            f"No se pudo leer la partida guardada:\n{SAVE_FILE}\n\nDetalle: {error}",
            10,
            76,
        )
        return None

    required = {
        "version", "status", "day", "phase", "war_turn", "survivors",
        "morale", "defense", "intel", "alliances", "resources", "decisions",
    }
    if not isinstance(state, dict) or not required.issubset(state):
        message("ARCHIVO DE CAMPAÑA", "La partida guardada no tiene el formato esperado. No se modificó.")
        return None
    if state["version"] != SAVE_VERSION:
        message(
            "VERSIÓN DE CAMPAÑA",
            "La partida fue creada por otra versión del módulo. Conservé el archivo sin modificar.",
        )
        return None
    state.setdefault("shortage_streak", 0)
    state.setdefault("preparation_turn", 1)
    return state


def status_text(state):
    r = state["resources"]
    return (
        f"Jornada: {state['day']}\n"
        f"Supervivientes: {state['survivors']}\n"
        f"Comida: {r['food']}   Agua: {r['water']}\n"
        f"Medicinas: {r['medicine']}   Materiales: {r['materials']}\n"
        f"Moral: {state['morale']}/10   Defensas: {state['defense']}/6\n"
        f"Inteligencia: {state['intel']}/6   Alianzas: {state['alliances']}/5\n"
        f"Escasez consecutiva: {state.get('shortage_streak', 0)}/2 jornadas"
    )


def ration_forecast_text(state):
    phase = state.get("phase")
    if phase == "war":
        turns_left = max(0, WAR_TURNS - state.get("war_turn", 1) + 1)
        base_rations = turns_left * WAR_RATION_COST
    elif phase == "preparation":
        prep_left = max(
            0,
            PREPARATION_TURNS - state.get("preparation_turn", 1) + 1,
        )
        base_rations = prep_left + WAR_TURNS * WAR_RATION_COST
    else:
        opening_phases_left = (
            len(EARLY_CAMPAIGN_PHASES) - EARLY_CAMPAIGN_PHASES.index(phase)
            if phase in EARLY_CAMPAIGN_PHASES
            else 0
        )
        base_rations = (
            opening_phases_left
            + PREPARATION_TURNS
            + WAR_TURNS * WAR_RATION_COST
        )

    resources = state["resources"]
    food = resources["food"]
    water = resources["water"]
    food_gap = max(0, base_rations - food)
    water_gap = max(0, base_rations - water)
    return (
        f"Raciones base restantes (incluye hoy): comida {base_rations}, agua {base_rations}.\n"
        f"Reservas {food}/{water}; sin reponer faltarían {food_gap}/{water_gap}. "
        "Los gastos de decisiones e incidentes son variables."
    )


def available(choices, state):
    result = []
    for choice in choices:
        requirements = choice.get("requires", {})
        if all(state["resources"].get(name, 0) >= amount for name, amount in requirements.items()):
            result.append(choice)
    return result


DECISION_STATS = {
    "stock_food": ("morale",),
    "fortify": ("defense",),
    "infirmary": ("morale",),
    "scouts": ("intel",),
    "food_run": ("intel", "survivors"),
    "water_run": ("intel", "survivors"),
    "medicine_run": ("intel",),
    "route_scout": ("intel",),
    "infested_depot": ("intel", "defense"),
    "crisis_fortify": ("defense",),
    "evacuate_zone": ("survivors", "intel"),
    "request_allies": ("alliances", "morale"),
    "investigate": ("intel",),
    "infested_pass": ("intel", "defense"),
    "prep_supply": ("survivors", "intel"),
    "prep_scavenge": ("intel", "defense"),
    "prep_trade": ("alliances", "intel"),
    "prep_fortify": ("defense",),
    "prep_clinic": ("survivors", "morale"),
    "prep_training": ("defense", "morale"),
    "treat_wounded": ("survivors", "morale"),
    "repair_homes": ("defense",),
    "rest": ("morale",),
    "ration_recovery": ("morale",),
    "welcome_refugees": ("alliances", "survivors"),
    "screen_refugees": ("intel",),
    "turn_refugees_away": ("defense", "morale"),
    "accept_unchecked": ("intel", "defense"),
    "negotiate": ("intel", "alliances"),
    "war_defend": ("defense",),
    "war_reinforce": ("alliances", "survivors"),
    "war_intel": ("intel",),
    "war_hold": ("defense", "morale"),
    "war_sabotage": ("intel", "defense"),
    "war_supply": ("intel", "survivors"),
    "final_hold": ("defense", "morale"),
    "final_talk": ("intel", "alliances"),
    "final_evacuate": ("survivors", "intel"),
}


def decision_success_probability(state, choice):
    risk = choice.get("risk")
    if risk:
        chance = (
            risk["success_chance"]
            + state["intel"] * risk.get("intel_bonus", 0)
            + state["defense"] * risk.get("defense_bonus", 0)
        )
    else:
        stats = DECISION_STATS.get(choice["id"], ("intel",))
        normalized = [
            state.get(name, 0) / STAT_LIMITS[name][1]
            for name in stats
        ]
        skill = sum(normalized) / len(normalized)
        chance = 0.70 + 0.20 * skill
    return max(0.05, min(0.95, chance))


def decision_stat_short_label(choice):
    stats = DECISION_STATS.get(choice.get("id"), ("intel",))
    return "/".join(STAT_SHORT_NAMES[name] for name in stats)


def compact_choice_hint(choice):
    hint = choice.get("hint", "")
    for full, short in (
        ("Supervivientes", "Sup."),
        ("Inteligencia", "Intel."),
        ("Defensas", "Def."),
        ("Materiales", "Mat."),
        ("Medicinas", "Med."),
        ("Comida", "Com."),
        ("Agua", "Ag."),
        ("Alianzas", "Al."),
    ):
        hint = hint.replace(full, short).replace(full.lower(), short)
    if choice.get("id") == "prep_supply":
        return "Mat.-1; Com.+3; Ag.+3"
    if choice.get("id") in ("prep_scavenge", "war_supply"):
        return "Riesgo; Com.+3; Ag.+2"
    if choice.get("id") == "prep_trade":
        return "Com.-2; Ag.-2; Med.-1; Mat.+2"
    if choice.get("id") == "war_sabotage":
        return "Riesgo; Intel. mejora éxito"
    if choice.get("id") in ("infested_depot", "war_sabotage"):
        return "Riesgo medio; Intel. mejora el éxito"
    if choice.get("id") == "accept_unchecked":
        return "Riesgo: puede ayudar o complicar el refugio"
    if choice.get("id") == "infested_pass":
        return "RIESGO EXTREMO: un fallo termina la campaña"
    return hint


def negative_changes(changes):
    result = {}
    resource_losses = {
        name: amount
        for name, amount in changes.get("resources", {}).items()
        if amount < 0
    }
    if resource_losses:
        result["resources"] = resource_losses
    for name, amount in changes.items():
        if name != "resources" and amount < 0:
            result[name] = amount
    return result


def merge_changes(*change_sets):
    merged = {}
    for changes in change_sets:
        for name, amount in changes.items():
            if name == "resources":
                resources = merged.setdefault("resources", {})
                for resource, delta in amount.items():
                    resources[resource] = resources.get(resource, 0) + delta
            else:
                merged[name] = merged.get(name, 0) + amount
    return merged


def effect_summary(state, changes):
    effects = []
    for resource, amount in changes.get("resources", {}).items():
        current = state["resources"][resource]
        applied = max(0, min(RESOURCE_LIMITS[resource], current + amount)) - current
        cap_note = " (límite)" if applied != amount else ""
        effects.append(f"{RESOURCE_NAMES[resource]} {applied:+d}{cap_note}")
    for stat, amount in changes.items():
        if stat == "resources":
            continue
        current = state[stat]
        low, high = STAT_LIMITS[stat]
        applied = max(low, min(high, current + amount)) - current
        cap_note = " (límite)" if applied != amount else ""
        effects.append(f"{STAT_NAMES[stat]} {applied:+d}{cap_note}")
    return ", ".join(effects) if effects else "sin cambios directos"


def risk_preview_text(state, choice):
    risk = choice["risk"]
    probability = decision_success_probability(state, choice)
    success_percent = int(round(probability * 100))
    failure_percent = 100 - success_percent
    success_changes = merge_changes(
        choice.get("changes", {}), risk.get("success_changes", {})
    )
    failure_changes = merge_changes(
        negative_changes(choice.get("changes", {})),
        risk.get("failure_changes", {}),
    )
    ration_cost = WAR_RATION_COST if state.get("phase") == "war" else 1
    preview = (
        f"Éxito {success_percent}% ({decision_stat_short_label(choice)}):\n"
        f"{risk.get('success_text', choice.get('result', 'La acción sale bien.'))}\n"
        f"Efectos directos: {effect_summary(state, success_changes)}.\n\n"
        f"Fallo {failure_percent}%:\n"
        f"{risk.get('failure_text', choice.get('failure_text', 'La acción falla.'))}\n"
        f"Efectos directos: {effect_summary(state, failure_changes)}.\n\n"
        f"Después se consumen {ration_cost} de comida y agua; un incidente aleatorio puede cambiar las reservas."
    )
    if choice.get("id") in {"infested_depot", "war_sabotage", "war_supply"}:
        preview += "\nSi sale bien, puede aparecer un minijuego opcional de bonificación."
    return preview


def choices_for(phase, state):
    if phase == "council":
        return [
            {
                "id": "stock_food",
                "label": "Asegurar raciones",
                "hint": "Comida +3; moral -1",
                "changes": {"resources": {"food": 3}, "morale": -1},
                "result": "Se reserva comida para los próximos días. El trabajo adicional desgasta a la comunidad.",
            },
            {
                "id": "fortify",
                "label": "Reforzar el perímetro",
                "hint": "Materiales -2; defensas +2",
                "requires": {"materials": 2},
                "changes": {"resources": {"materials": -2}, "defense": 2},
                "result": "El perímetro queda mejor preparado para resistir una ofensiva.",
            },
            {
                "id": "infirmary",
                "label": "Organizar la enfermería",
                "hint": "Medicinas -1; moral +2",
                "requires": {"medicine": 1},
                "changes": {"resources": {"medicine": -1}, "morale": 2},
                "result": "La atención a los heridos reduce la tensión dentro del refugio.",
            },
            {
                "id": "scouts",
                "label": "Enviar observadores",
                "hint": "Inteligencia +1; moral -1",
                "changes": {"intel": 1, "morale": -1},
                "result": "Los observadores registran movimientos en los caminos, aunque su ausencia preocupa a la comunidad.",
            },
        ]

    if phase == "expedition":
        return [
            {
                "id": "food_run",
                "label": "Buscar alimentos",
                "hint": "Comida +4; moral -1",
                "changes": {"resources": {"food": 4}, "morale": -1},
                "result": "La expedición vuelve con raciones y deja marcado un camino que habrá que vigilar.",
            },
            {
                "id": "water_run",
                "label": "Asegurar agua",
                "hint": "Agua +4; moral -1",
                "changes": {"resources": {"water": 4}, "morale": -1},
                "result": "El grupo regresa con agua suficiente para sostener la actividad del refugio.",
            },
            {
                "id": "medicine_run",
                "label": "Revisar un puesto médico",
                "hint": "Medicinas +2; comida -1; moral -1",
                "changes": {"resources": {"medicine": 2, "food": -1}, "morale": -1},
                "result": "Se recuperan suministros médicos, a costa de consumir parte de las reservas.",
            },
            {
                "id": "route_scout",
                "label": "Reconocer rutas",
                "hint": "Inteligencia +2; moral -1",
                "changes": {"intel": 2, "morale": -1},
                "result": "El grupo vuelve con información útil sobre los accesos y movimientos cercanos.",
            },
            {
                "id": "infested_depot",
                "label": "Entrar al depósito infestado",
                "hint": "Riesgo medio; inteligencia mejora la probabilidad de éxito",
                "risk": {
                    "success_chance": 0.68,
                    "intel_bonus": 0.035,
                    "defense_bonus": 0.015,
                    "success_changes": {"resources": {"food": 3, "medicine": 1}},
                    "success_text": "El equipo logra entrar y vuelve con comida y medicinas.",
                    "failure_changes": {"survivors": -3, "morale": -2},
                    "failure_text": "La alarma atrae caminantes y el grupo regresa con bajas.",
                },
                "changes": {},
                "result": "La expedición intenta alcanzar un depósito rodeado de caminantes.",
            },
        ]

    if phase == "crisis":
        return [
            {
                "id": "crisis_fortify",
                "label": "Cerrar accesos expuestos",
                "hint": "Materiales -1; defensas +2; moral -1",
                "requires": {"materials": 1},
                "changes": {"resources": {"materials": -1}, "defense": 2, "morale": -1},
                "result": "La comunidad concentra sus fuerzas en un perímetro más fácil de defender.",
            },
            {
                "id": "evacuate_zone",
                "label": "Evacuar la zona exterior",
                "hint": "Supervivientes -1; moral +2; inteligencia +1",
                "changes": {"survivors": -1, "morale": 2, "intel": 1},
                "result": "La zona expuesta se abandona a tiempo. La comunidad pierde una persona en la retirada, pero obtiene información de la amenaza.",
            },
            {
                "id": "request_allies",
                "label": "Pedir apoyo a una comunidad vecina",
                "hint": "Comida -1; alianzas +1; moral +1",
                "changes": {"resources": {"food": -1}, "alliances": 1, "morale": 1},
                "result": "Una comunidad vecina acepta coordinarse. Compartir la noticia también consume reservas.",
            },
            {
                "id": "investigate",
                "label": "Investigar el origen de la alarma",
                "hint": "Medicinas -1; inteligencia +2",
                "requires": {"medicine": 1},
                "changes": {"resources": {"medicine": -1}, "intel": 2},
                "result": "La investigación aclara por dónde puede llegar el peligro.",
            },
            {
                "id": "infested_pass",
                "label": "Cruzar el paso infestado",
                "hint": "PELIGRO EXTREMO: un fracaso puede terminar la campaña",
                "risk": {
                    "success_chance": 0.72,
                    "intel_bonus": 0.035,
                    "defense_bonus": 0.025,
                    "success_changes": {"resources": {"materials": 2, "food": 2}, "intel": 1},
                    "success_text": "La columna cruza sin quedar rodeada y recupera materiales y provisiones.",
                    "failure_changes": {"survivors": -12, "morale": -3, "defense": -1},
                    "failure_text": "La columna queda atrapada en el paso. El refugio pierde a todos sus supervivientes.",
                },
                "changes": {},
                "result": "Una columna intenta abrirse paso por una ruta bloqueada.",
            },
        ]

    if phase == "recovery":
        return [
            {
                "id": "treat_wounded",
                "label": "Atender a los heridos",
                "hint": "Medicinas -1; supervivientes +1; moral +1",
                "requires": {"medicine": 1},
                "changes": {"resources": {"medicine": -1}, "survivors": 1, "morale": 1},
                "result": "La enfermería estabiliza a una persona y devuelve algo de confianza al grupo.",
            },
            {
                "id": "repair_homes",
                "label": "Reparar las viviendas",
                "hint": "Materiales -2; defensas +1; moral +1",
                "requires": {"materials": 2},
                "changes": {"resources": {"materials": -2}, "defense": 1, "morale": 1},
                "result": "Las reparaciones mejoran los refugios y ayudan a la comunidad a recuperar su rutina.",
            },
            {
                "id": "rest",
                "label": "Dar un día de descanso",
                "hint": "Moral +2; inteligencia -1",
                "changes": {"morale": 2, "intel": -1},
                "result": "La gente descansa, aunque se retrasa el análisis de los movimientos enemigos.",
            },
            {
                "id": "ration_recovery",
                "label": "Repartir una comida caliente",
                "hint": "Comida -2; agua -1; moral +3",
                "requires": {"food": 2, "water": 1},
                "changes": {"resources": {"food": -2, "water": -1}, "morale": 3},
                "result": "La comida compartida fortalece la moral del refugio.",
            },
        ]

    if phase == "refugees":
        return [
            {
                "id": "welcome_refugees",
                "label": "Dar lugar a las familias",
                "hint": "Comida -2; agua -2; supervivientes +2; moral +1",
                "requires": {"food": 2, "water": 2},
                "changes": {
                    "resources": {"food": -2, "water": -2},
                    "survivors": 2,
                    "morale": 1,
                },
                "result": "Las familias se integran al refugio y se suman a sus tareas.",
            },
            {
                "id": "screen_refugees",
                "label": "Revisar al grupo antes de aceptarlo",
                "hint": "Inteligencia +1; medicinas -1; supervivientes +1",
                "requires": {"medicine": 1},
                "changes": {
                    "resources": {"medicine": -1},
                    "intel": 1,
                    "survivors": 1,
                    "morale": -1,
                },
                "result": "La revisión reduce la incertidumbre, aunque la demora genera desconfianza.",
            },
            {
                "id": "turn_refugees_away",
                "label": "No abrir el refugio",
                "hint": "Defensas +1; moral -2; alianzas -1",
                "changes": {"defense": 1, "morale": -2, "alliances": -1},
                "result": "El grupo sigue de largo. El perímetro queda controlado, pero la decisión divide a la comunidad.",
            },
            {
                "id": "accept_unchecked",
                "label": "Dejar entrar a todos sin revisar",
                "hint": "Riesgo: puede traer ayuda o un problema al refugio",
                "risk": {
                    "success_chance": 0.70,
                    "intel_bonus": 0.025,
                    "defense_bonus": 0.015,
                    "success_changes": {
                        "survivors": 3,
                        "resources": {"food": 2},
                        "alliances": 1,
                    },
                    "success_text": "El grupo trae provisiones y se integra a la comunidad.",
                    "failure_changes": {"survivors": -4, "morale": -2},
                    "failure_text": "Una persona infectada provoca pánico y varias bajas.",
                },
                "changes": {},
                "result": "La decisión se toma sin tiempo para revisar al grupo.",
            },
        ]

    if phase == "preparation":
        return [
            {
                "id": "prep_supply",
                "label": "Reponer comida y agua",
                "hint": "Materiales -1; comida +3; agua +3",
                "requires": {"materials": 1},
                "changes": {"resources": {"materials": -1, "food": 3, "water": 3}},
                "result": "El grupo repara los recipientes y deja listas nuevas raciones para los días de guerra.",
            },
            {
                "id": "prep_scavenge",
                "label": "Rastrear depósito",
                "hint": "Riesgo medio; si sale bien, comida +3 y agua +2",
                "risk": {
                    "success_chance": 0.66,
                    "intel_bonus": 0.035,
                    "defense_bonus": 0.015,
                    "success_changes": {"resources": {"food": 3, "water": 2}},
                    "success_text": "La cuadrilla recupera provisiones antes de que llegue la ofensiva.",
                    "failure_changes": {"survivors": -1, "morale": -1},
                    "failure_text": "El depósito estaba vigilado y la cuadrilla vuelve con una baja.",
                },
                "changes": {},
                "result": "Una cuadrilla intenta recuperar provisiones en una zona expuesta.",
            },
            {
                "id": "prep_trade",
                "label": "Cambiar por equipo",
                "hint": "Comida -2; agua -2; medicinas -1; materiales +2",
                "requires": {"food": 2, "water": 2, "medicine": 1},
                "changes": {
                    "resources": {"food": -2, "water": -2, "medicine": -1, "materials": 2}
                },
                "result": "El asentamiento vecino entrega piezas y herramientas a cambio de provisiones médicas.",
            },
            {
                "id": "prep_fortify",
                "label": "Instalar trampas",
                "hint": "Materiales -2; defensas +1; inteligencia +1",
                "requires": {"materials": 2},
                "changes": {"resources": {"materials": -2}, "defense": 1, "intel": 1},
                "result": "Las entradas quedan cubiertas y los vigías aprenden a reconocer los puntos débiles.",
            },
            {
                "id": "prep_clinic",
                "label": "Abrir enfermería",
                "hint": "Medicinas -1; supervivientes +1; moral +1",
                "requires": {"medicine": 1},
                "changes": {"resources": {"medicine": -1}, "survivors": 1, "morale": 1},
                "result": "La enfermería estabiliza a una persona herida y organiza suministros para la ofensiva.",
            },
            {
                "id": "prep_training",
                "label": "Entrenar a la guardia",
                "hint": "Comida -1; defensas +1; moral -1",
                "requires": {"food": 1},
                "changes": {"resources": {"food": -1}, "defense": 1, "morale": -1},
                "result": "La guardia practica relevos y señales para sostener el perímetro durante los ataques.",
            },
        ]

    if phase == "war":
        negotiation = {
            "id": "negotiate",
            "label": "Abrir una negociación",
            "hint": "Medicinas -1; resultado depende de inteligencia y alianzas",
            "requires": {"medicine": 1},
            "changes": {"resources": {"medicine": -1}},
        }
        if state["intel"] >= 2 or state["alliances"] >= 1:
            negotiation["changes"].update({"alliances": 1, "morale": 1})
            negotiation["result"] = "La información y los contactos permiten negociar desde una posición más firme."
        else:
            negotiation["changes"].update({"intel": 1, "morale": -1})
            negotiation["result"] = "La negociación no consigue apoyo todavía, pero permite observar mejor a la otra parte."
        return [
            {
                "id": "war_defend",
                "label": "Sostener las defensas",
                "hint": "Materiales -1; defensas +2; moral -1",
                "requires": {"materials": 1},
                "changes": {"resources": {"materials": -1}, "defense": 2, "morale": -1},
                "result": "El perímetro resiste este turno; el esfuerzo reduce la moral.",
            },
            {
                "id": "war_reinforce",
                "label": "Movilizar refuerzos",
                "hint": "Comida -1; alianzas +1; moral +1",
                "requires": {"food": 1},
                "changes": {"resources": {"food": -1}, "alliances": 1, "morale": 1},
                "result": "Más personas se suman a la defensa y la comunidad recupera confianza.",
            },
            {
                "id": "war_intel",
                "label": "Reconocer posiciones",
                "hint": "Agua -1; inteligencia +2; moral -1",
                "requires": {"water": 1},
                "changes": {"resources": {"water": -1}, "intel": 2, "morale": -1},
                "result": "La información mejora las decisiones del próximo turno, aunque la salida desgasta al grupo.",
            },
            negotiation,
            {
                "id": "war_hold",
                "label": "Mantener la línea",
                "hint": "Defensas +1; moral -1",
                "changes": {"defense": 1, "morale": -1},
                "result": "La línea se mantiene con el esfuerzo de quienes siguen en el frente.",
            },
            {
                "id": "war_sabotage",
                "label": "Sabotear suministros",
                "hint": "Riesgo medio: la inteligencia mejora la probabilidad de éxito",
                "risk": {
                    "success_chance": 0.62,
                    "intel_bonus": 0.035,
                    "defense_bonus": 0.012,
                    "success_changes": {"resources": {"materials": 2, "medicine": 1}, "intel": 1},
                    "success_text": "La infiltración sale bien y retrasa una parte de la ofensiva.",
                    "failure_changes": {"survivors": -4, "defense": -1, "morale": -2},
                    "failure_text": "El grupo queda expuesto y vuelve con bajas.",
                },
                "changes": {},
                "result": "Un equipo intenta entrar en una zona controlada por los Salvadores.",
            },
            {
                "id": "war_supply",
                "label": "Recuperar un convoy",
                "hint": "Riesgo medio; si sale bien, comida +3 y agua +2",
                "risk": {
                    "success_chance": 0.62,
                    "intel_bonus": 0.035,
                    "defense_bonus": 0.015,
                    "success_changes": {"resources": {"food": 3, "water": 2}},
                    "success_text": "El equipo vuelve con provisiones suficientes para sostener a la comunidad.",
                    "failure_changes": {"survivors": -2, "morale": -1},
                    "failure_text": "El convoy estaba bajo fuego y el grupo vuelve con bajas, sin provisiones.",
                },
                "changes": {},
                "result": "Una salida de abastecimiento puede aliviar las reservas, pero expone al equipo.",
            },
        ]

    return []


def apply_changes(state, changes):
    for name, amount in changes.get("resources", {}).items():
        limit = RESOURCE_LIMITS[name]
        state["resources"][name] = max(0, min(limit, state["resources"][name] + amount))
    for name in ("survivors", "morale", "defense", "intel", "alliances"):
        if name in changes:
            low, high = STAT_LIMITS[name]
            state[name] = max(low, min(high, state[name] + changes[name]))


def resolve_choice(state, choice):
    success_chance = decision_success_probability(state, choice)
    success_percent = int(round(success_chance * 100))
    failure_percent = 100 - success_percent
    probability_text = (
        f"Probabilidad estimada: {success_percent}% éxito / "
        f"{failure_percent}% fallo."
    )
    risk = choice.get("risk")

    if random.random() < success_chance:
        apply_changes(state, choice.get("changes", {}))
        if risk:
            apply_changes(state, risk.get("success_changes", {}))
            result = risk["success_text"]
        else:
            result = choice["result"]
        return f"{probability_text}\n\nÉXITO: {result}"

    apply_changes(state, negative_changes(choice.get("changes", {})))
    if risk:
        apply_changes(state, risk.get("failure_changes", {}))
        result = risk["failure_text"]
    else:
        apply_changes(state, choice.get("failure_changes", {"morale": -1}))
        result = choice.get(
            "failure_text",
            "La maniobra falla: no se alcanza el objetivo, se pierde tiempo "
            "y la comunidad siente el desgaste.",
        )
    return f"{probability_text}\n\nFALLO: {result}"


def resolve_random_incident(state):
    if random.random() >= INCIDENT_CHANCE:
        return ""

    incident = random.choice(
        ("cache", "herd", "injury", "refugees", "radio", "spoiled")
    )
    if incident == "cache":
        resource = random.choice(tuple(RESOURCE_NAMES))
        before = state["resources"][resource]
        amount = random.randint(1, 3)
        apply_changes(state, {"resources": {resource: amount}})
        gained = state["resources"][resource] - before
        return f"Hallazgo aleatorio: encontraron {gained} de {RESOURCE_NAMES[resource].lower()}."

    if incident == "herd":
        if state["defense"] >= 3:
            apply_changes(state, {"resources": {"materials": -1}})
            return "Incidente aleatorio: una horda golpeó el perímetro; las defensas resistieron, pero se perdió material."
        casualties = random.randint(1, 2)
        apply_changes(state, {"survivors": -casualties, "morale": -1})
        return f"Incidente aleatorio: una horda atravesó un acceso y hubo {casualties} baja(s)."

    if incident == "injury":
        if state["resources"]["medicine"] > 0:
            apply_changes(state, {"resources": {"medicine": -1}})
            return "Incidente aleatorio: una persona resultó herida; la enfermería pudo atenderla."
        apply_changes(state, {"survivors": -1, "morale": -1})
        return "Incidente aleatorio: una persona resultó herida y no había medicinas disponibles."

    if incident == "refugees":
        if state["resources"]["food"] >= 2 and state["resources"]["water"] >= 2:
            apply_changes(
                state,
                {"survivors": 1, "morale": 1, "resources": {"food": -1, "water": -1}},
            )
            return "Incidente aleatorio: una persona refugiada se suma al grupo y comparte información."
        apply_changes(state, {"morale": -1})
        return "Incidente aleatorio: una persona pide refugio, pero las reservas no alcanzan."

    if incident == "radio":
        if state["intel"] >= 2:
            apply_changes(state, {"alliances": 1, "morale": 1})
            return "Incidente aleatorio: una transmisión permite coordinarse con una comunidad vecina."
        apply_changes(state, {"intel": 1})
        return "Incidente aleatorio: se intercepta una transmisión con datos parciales."

    if state["intel"] >= 4:
        apply_changes(state, {"intel": -1})
        return "Incidente aleatorio: se detectó un intento de sabotaje a tiempo y la reserva quedó intacta."

    resource = random.choice(("food", "water"))
    amount = random.randint(1, 2)
    before = state["resources"][resource]
    apply_changes(state, {"resources": {resource: -amount}})
    lost = before - state["resources"][resource]
    return f"Incidente aleatorio: alguien contaminó una reserva; se perdió {lost} de {RESOURCE_NAMES[resource].lower()}."


def failure_reason(state):
    if state["survivors"] <= 0:
        return "La comunidad perdió a todos sus supervivientes."
    if state["morale"] <= 0 and state["defense"] <= 0:
        return "La moral y las defensas llegaron a cero; el refugio se desintegró."
    return ""


def campaign_epilogue(state, title, final_choice=None, failure=""):
    survivors = state.get("survivors", 0)
    alliances = state.get("alliances", 0)
    if alliances >= 2:
        alliance_preparation = "comunidades dispuestas a sostenerse entre sí"
        route_support = "Las comunidades aliadas cerraron las rutas de retirada."
    elif alliances == 1:
        alliance_preparation = "un asentamiento vecino dispuesto a cooperar"
        route_support = "El asentamiento aliado cerró una de las rutas de retirada."
    else:
        alliance_preparation = "una defensa preparada para sostenerse sin apoyo externo"
        route_support = "Los defensores locales cubrieron las rutas de retirada."

    if failure:
        if survivors <= 0:
            return (
                "El último registro termina cuando la comunidad perdió a todos sus "
                "supervivientes. Las reservas y las rutas de salida no alcanzaron para "
                "organizar otra retirada. El refugio quedó en silencio, y no hubo un "
                "grupo que pudiera reclamarlo ni volver a abrir sus puertas.\n\n"
                "Esta línea alternativa no continúa con una reconstrucción: la campaña "
                "se corta acá. El archivo conserva la causa de la caída para que la "
                "siguiente partida pueda tomar otro camino."
            )
        return (
            "El refugio no se desarmó por un único ataque. La moral y las defensas "
            "habían caído al mismo tiempo; las órdenes dejaron de coordinarse y cada "
            "familia buscó una salida distinta. El asentamiento se vació antes de que "
            "Rick pudiera reunir a todos para una retirada común.\n\n"
            f"Al cerrarse el registro quedaban {survivors} supervivientes, pero ya no "
            "había una comunidad capaz de sostener el refugio. Algunos tomaron caminos "
            "separados y otros siguieron a Rick hacia terreno abierto. La campaña termina "
            "con esa dispersión, no con una victoria que el grupo todavía no podía "
            "alcanzar."
        )

    if title == "RETIRADA DEL REFUGIO":
        return (
            "La orden de evacuación llegó antes de que el cerco se cerrara. Rick hizo "
            "dejar atrás las paredes y cargar lo que podía acompañar a la comunidad: "
            "medicinas, herramientas, agua y el registro de quienes habían vivido allí. "
            "La retirada no fue una derrota limpia; hubo demoras, discusiones y gente que "
            "tuvo que volver sobre sus pasos para ayudar a los demás.\n\n"
            "El grupo salió unido. Durante las semanas siguientes avanzó por rutas "
            "secundarias y armó campamentos breves, sin volver a depender de una sola "
            "entrada o de un muro. La primera noche segura no trajo festejos: trajo una "
            "lista de tareas y un lugar para descansar.\n\n"
            f"Al terminar la campaña quedaban {survivors} supervivientes. La historia "
            "de Alexandria, en esta versión, no acaba con la caída de sus edificios: "
            "continúa como una comunidad que aprende a moverse y a elegir dónde volver "
            "a echar raíces."
        )

    if title == "VICTORIA ESTRATÉGICA":
        if final_choice == "talk":
            return (
                "Rick llegó a la mesa con algo que Negan no esperaba: rutas vigiladas, "
                "reservas suficientes para no aceptar cualquier condición y "
                f"{alliance_preparation}. La negociación no fue una rendición. "
                "Las condiciones pusieron fin a los tributos y a las incursiones; Negan "
                "entregó sus armas y quedó bajo custodia, mientras los Salvadores "
                "aceptaban retirarse de los asentamientos.\n\n"
                "El acuerdo no convirtió a los enemigos en amigos. Cada comunidad "
                "mantuvo sus propias decisiones y se estableció una mesa común para "
                "resolver disputas antes de que volvieran a convertirse en una guerra. "
                "Las primeras semanas se ocuparon de reparar casas, repartir suministros "
                "y buscar a quienes habían quedado aislados.\n\n"
                f"Años después, los caminos entre los asentamientos volvieron a tener "
                f"intercambio y vigilancia compartida. Con {survivors} personas en el "
                "refugio al cierre de la campaña, Rick pudo imaginar un futuro en el que "
                "la seguridad dependía de acuerdos sostenidos, no de un solo líder."
            )
        return (
            "La última ofensiva encontró un perímetro preparado. Los observadores "
            "anticiparon los accesos y las defensas frenaron el avance. "
            f"{route_support} Rick evitó convertir la victoria en "
            "una persecución sin fin: pidió que los Salvadores dejaran las armas y "
            "aceptaran el fin de los ataques. Negan quedó bajo custodia, con vigilancia "
            "acordada entre las comunidades.\n\n"
            "La victoria no devolvió lo perdido, pero impidió que la guerra siguiera "
            "decidiendo quién podía vivir detrás de un muro. Alexandria, Hilltop y los "
            "demás refugios comenzaron a reparar caminos y a compartir alimentos y "
            "medicinas. Rick tuvo que aprender que sostener la paz exigía tantas "
            "decisiones como sostener una defensa.\n\n"
            f"Años después, los asentamientos seguían siendo distintos, pero ya no "
            f"estaban aislados. {survivors} supervivientes cerraron esta campaña con "
            "una victoria construida en equipo; en esta línea alternativa, esa alianza "
            "fue el comienzo de una etapa nueva."
        )

    if title == "VICTORIA CON PÉRDIDAS":
        return (
            "El refugio resistió, pero el costo se hizo visible cuando terminó el ruido. "
            "Faltaban personas en los puestos, varias viviendas quedaron inutilizables "
            "y las reservas tuvieron que repartirse con cuidado. Rick ordenó atender a "
            "los heridos y registrar cada nombre antes de discutir qué hacer con Negan "
            "y con los Salvadores que seguían en pie.\n\n"
            "La comunidad obtuvo una victoria, aunque nadie la confundió con volver a "
            "la vida anterior. Los supervivientes retiraron escombros y vigilaron las "
            "rutas; quienes habían llegado a cooperar también aportaron lo que podían. "
            "La respuesta de Rick fue reconstruir con reglas compartidas y no perseguir "
            "a todos los que habían combatido del otro lado.\n\n"
            f"Con {survivors} supervivientes al final de la campaña, la victoria abrió "
            "un futuro posible, pero dejó una obligación: recordar el precio y evitar "
            "que la reconstrucción preparara la próxima guerra."
        )

    if title == "RETIRADA NEGOCIADA":
        if final_choice == "talk":
            return (
                "La negociación consiguió una pausa, no una solución completa. Rick "
                "obtuvo una salida para el grupo y el cese de los ataques mientras los "
                "supervivientes abandonaban el terreno que ya no podían defender. Las "
                "condiciones quedaron débiles: ninguno de los dos bandos confiaba en que "
                "la otra parte las respetara para siempre.\n\n"
                "En lugar de volver a ocupar el mismo lugar, la comunidad avanzó hacia "
                "refugios más pequeños y mantuvo contacto por radio con los asentamientos cercanos. "
                "Rick dejó claro que esa retirada era una decisión para salvar vidas, "
                "no una promesa de obediencia.\n\n"
                f"Al cierre, {survivors} personas seguían juntas. La paz de esta línea "
                "alternativa era frágil, pero alcanzó para que pudieran elegir el "
                "próximo paso."
            )
        return (
            "La defensa ganó tiempo, pero no podía sostener otra ofensiva. Rick entendió "
            "que insistir en cada pared iba a convertir una retirada difícil en una "
            "pérdida mayor. Aceptó una pausa negociada y organizó la salida mientras "
            "quedaba una ruta abierta; parte de los suministros y del terreno quedó atrás.\n\n"
            "La comunidad tardó en decidir si aquello había sido una retirada o una "
            "derrota. Con el paso de los días, la discusión cedió ante tareas concretas: "
            "encontrar agua, reparar el equipo y volver a contactar a los grupos aliados. "
            "El conflicto no quedó resuelto, pero dejó de ocupar cada hora del día.\n\n"
            f"{survivors} supervivientes siguieron adelante. En esta versión de la "
            "historia, el refugio perdió su territorio y conservó la posibilidad de "
            "construir otro."
        )

    return (
        "La última defensa no alcanzó para sostener el asentamiento. Cuando se abrió "
        "una brecha, las órdenes llegaron tarde y los grupos empezaron a separarse. "
        "Rick condujo a quienes todavía podía reunir por una salida secundaria; detrás "
        "quedaron las reservas, los puestos y el lugar que habían intentado proteger.\n\n"
        "La dispersión volvió más difícil encontrarse y dejó a cada grupo expuesto a "
        "sus propios riesgos. No hubo una marcha triunfal ni un acuerdo que cerrara la "
        "guerra. Hubo decisiones pequeñas: compartir agua, esperar a quien se había "
        "quedado atrás y seguir avanzando antes de que la ruta volviera a quedar bloqueada.\n\n"
        f"El registro termina con {survivors} supervivientes y el refugio perdido. "
        "La campaña queda marcada como una derrota; si la historia continúa, tendrá "
        "que empezar desde los caminos y no desde las murallas."
    )


def finish_if_failed(state):
    reason = failure_reason(state)
    if not reason:
        return ""
    state["status"] = "failed"
    state["ending"] = {
        "title": "EL REFUGIO CAE",
        "score": 0,
        "text": reason,
        "epilogue": campaign_epilogue(state, "EL REFUGIO CAE", failure=reason),
    }
    return reason


def consume_rations(state):
    shortages = []
    ration_cost = WAR_RATION_COST if state.get("phase") == "war" else 1
    for resource, label in (("food", "comida"), ("water", "agua")):
        if state["resources"][resource] >= ration_cost:
            state["resources"][resource] -= ration_cost
        else:
            state["resources"][resource] = 0
            state["morale"] = max(0, state["morale"] - 1)
            shortages.append(label)

    if shortages:
        state["shortage_streak"] = state.get("shortage_streak", 0) + 1
    else:
        state["shortage_streak"] = 0

    result = (
        "El frente consumió dos raciones de comida y agua."
        if ration_cost > 1
        else "Se consumió una ración de comida y agua."
    )
    if shortages:
        result = "La reserva de " + " y ".join(shortages) + " se agotó; la moral baja."
    if state["shortage_streak"] >= 2:
        apply_changes(state, {"survivors": -1})
        state["shortage_streak"] = 0
        result += " La escasez prolongada causa una baja."
    return result


def phase_label(state):
    phase = state["phase"]
    if phase == "war":
        return f"GUERRA — TURNO {state['war_turn']} DE {WAR_TURNS}"
    if phase == "preparation":
        return f"PREPARACIÓN — JORNADA {state.get('preparation_turn', 1)} DE {PREPARATION_TURNS}"
    return PHASES.get(phase, ("THE REFUGE", ""))[0]


def advance(state):
    phase = state["phase"]
    if phase == "council":
        state["phase"] = "expedition"
    elif phase == "expedition":
        state["phase"] = "crisis"
    elif phase == "crisis":
        state["phase"] = "recovery"
    elif phase == "recovery":
        state["phase"] = "refugees"
    elif phase == "refugees":
        state["phase"] = "preparation"
        state["preparation_turn"] = 1
    elif phase == "preparation":
        if state.get("preparation_turn", 1) < PREPARATION_TURNS:
            state["preparation_turn"] = state.get("preparation_turn", 1) + 1
        else:
            state["phase"] = "war"
            state["war_turn"] = 1
    elif phase == "war":
        if state["war_turn"] < WAR_TURNS:
            state["war_turn"] += 1
        else:
            state["phase"] = "final"
    state["day"] += 1


def record_decision(state, phase, choice, outcome):
    state["decisions"].append({
        "day": state["day"],
        "phase": phase,
        "choice": choice,
        "outcome": outcome,
    })


def ending_score(state):
    r = state["resources"]
    return (
        state["defense"] * 2
        + state["intel"] * 2
        + state["alliances"] * 3
        + state["morale"]
        + min(r["food"], 4)
        + min(r["water"], 4)
        + min(r["medicine"], 2)
        + state["survivors"] // 2
    )


ARENA_WIDTH = 40
ARENA_HEIGHT = 14
ARENA_DURATION = 40.0
ARENA_WAVES = 1
ARENA_LIVES = 2
ARENA_SPAWN_SCHEDULE = (
    (2.5, "S"),
    (5.0, "N"),
    (7.5, "Z"),
    (10.0, "S"),
    (12.5, "N"),
    (15.0, "Z"),
    (17.5, "S"),
    (20.0, "N"),
    (22.5, "Z"),
    (25.0, "S"),
    (27.5, "N"),
    (30.0, "Z"),
    (32.5, "S"),
    (35.0, "N"),
    (37.5, "Z"),
)
ARENA_SPEEDUP_PER_SECOND = 0.003
ARENA_MIN_SPEED_FACTOR = 0.88
ARENA_WALLS = {
    (5, 2), (6, 2), (5, 3), (6, 3),
    (13, 2), (14, 2), (13, 3), (14, 3),
    (26, 2), (27, 2), (26, 3), (27, 3),
    (34, 3), (35, 3), (34, 4), (35, 4),
    (8, 7), (9, 7), (8, 8), (9, 8),
    (17, 10), (18, 10), (17, 11), (18, 11),
    (25, 7), (26, 7), (25, 8), (26, 8),
    (33, 10), (34, 10), (33, 11), (34, 11),
    (4, 10), (5, 10), (4, 11), (5, 11),
    (20, 3), (21, 3), (20, 4), (21, 4),
}
ARENA_SPAWNS = (
    (1, 1), (ARENA_WIDTH - 2, ARENA_HEIGHT - 2),
    (1, ARENA_HEIGHT - 2), (ARENA_WIDTH - 2, 1),
    (ARENA_WIDTH // 2, 0), (ARENA_WIDTH // 2, ARENA_HEIGHT - 1),
)
ARENA_MOVES = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}
ARENA_ARROW_KEYS = {
    b"A": "w",
    b"B": "s",
    b"C": "d",
    b"D": "a",
}


def _arena_read_key(fd):
    first = os.read(fd, 1)
    if first != b"\x1b":
        return first.decode("ascii", errors="ignore").lower()

    ready, _, _ = select.select([fd], [], [], 0.05)
    if not ready:
        return ""
    prefix = os.read(fd, 1)
    if prefix not in (b"[", b"O"):
        return ""

    ready, _, _ = select.select([fd], [], [], 0.05)
    if not ready:
        return ""
    return ARENA_ARROW_KEYS.get(os.read(fd, 1), "")


@contextmanager
def _minigame_terminal():
    if not sys.stdin.isatty():
        yield None
        return

    fd = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        quiet_settings = termios.tcgetattr(fd)
        quiet_settings[3] &= ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, quiet_settings)
        while select.select([fd], [], [], 0)[0]:
            os.read(fd, 1)
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()
        yield fd
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous_settings)
        sys.stdout.write("\x1b[?25h\x1b[2J\x1b[H")
        sys.stdout.flush()


def _minigame_wait_key(fd, timeout, on_tick=None):
    deadline = time.monotonic() + timeout
    next_tick = 0.0
    while True:
        now = time.monotonic()
        remaining = deadline - now
        if remaining <= 0:
            return ""
        if on_tick and now >= next_tick:
            on_tick(remaining)
            next_tick = now + 0.12
        ready, _, _ = select.select([fd], [], [], min(remaining, 0.12))
        if ready:
            pressed = _arena_read_key(fd)
            if pressed:
                return pressed


def _minigame_color(text, color="white", bold=False):
    if not MINIGAME_COLOR_ENABLED:
        return text
    code = MINIGAME_COLOR_CODES.get(color, MINIGAME_COLOR_CODES["white"])
    style = f"1;{code}" if bold else code
    return f"\x1b[{style}m{text}\x1b[0m"


def _write_centered_screen(lines):
    columns, rows = shutil.get_terminal_size(fallback=(80, 24))
    visible_width = max((len(plain) for plain, _ in lines), default=0)
    top = max(0, (rows - len(lines)) // 2)
    left = max(0, (columns - visible_width) // 2)
    output = ["\x1b[H\x1b[J", "\n" * top]
    for index, (plain, styled) in enumerate(lines):
        padding = max(0, (visible_width - len(plain)) // 2)
        trailing = max(0, visible_width - len(plain) - padding)
        line = " " * (left + padding) + styled + " " * trailing
        if index < len(lines) - 1:
            line += "\n"
        output.append(line)
    sys.stdout.write("".join(output))
    sys.stdout.flush()


def _render_minigame_panel(title, content, accent="cyan", footer=""):
    columns, _ = shutil.get_terminal_size(fallback=(80, 24))
    wrap_width = max(12, min(64, columns - 16))
    rows = []
    for item in content:
        text, color = item if isinstance(item, tuple) else (item, "white")
        wrapped = textwrap.wrap(
            str(text),
            width=wrap_width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]
        rows.extend((line, color) for line in wrapped)
    if footer:
        rows.extend([("", "dim"), (footer, "dim")])

    title_lines = textwrap.wrap(title, width=wrap_width) or [""]
    longest_line = max(
        [*(len(line) for line, _ in rows), *(len(line) for line in title_lines)],
        default=0,
    )
    box_width = min(columns - 4, max(44, longest_line + 6))
    top = ("╔" + "═" * (box_width - 2) + "╗", "cyan")
    separator = ("╟" + "─" * (box_width - 2) + "╢", "dim")
    bottom = ("╚" + "═" * (box_width - 2) + "╝", "cyan")
    screen_lines = []
    screen_lines.append((top[0], _minigame_color(top[0], accent, True)))

    for index, line in enumerate(title_lines):
        padded = "║ " + line.center(box_width - 4) + " ║"
        screen_lines.append((padded, _minigame_color(padded, accent, True)))
    screen_lines.append((separator[0], _minigame_color(separator[0], "dim")))
    for line, color in rows:
        padded = "║  " + line.ljust(box_width - 6) + "  ║"
        screen_lines.append((padded, _minigame_color(padded, color)))
    screen_lines.append((bottom[0], _minigame_color(bottom[0], accent, True)))
    _write_centered_screen(screen_lines)


def _minigame_bar(current, total, width=18):
    if total <= 0:
        filled = 0
    else:
        filled = max(0, min(width, int(width * current / total)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _direction_glyph(key):
    return {"w": "↑", "a": "←", "s": "↓", "d": "→"}[key]


def _direction_sequence_game(title, count=4, time_limit=7.0):
    sequence = [random.choice(tuple(ARENA_MOVES)) for _ in range(count)]
    with _minigame_terminal() as fd:
        if fd is None:
            return False

        shown = "    ".join(_direction_glyph(key) for key in sequence)
        _render_minigame_panel(
            title,
            [
                ("MEMORIZÁ LA RUTA", "yellow"),
                (shown, "white"),
                (f"SECUENCIA DE {count} MOVIMIENTOS", "dim"),
            ],
            accent="cyan",
            footer="FLECHAS O W A S D  ·  PREPARATE",
        )
        time.sleep(1.4 + count * 0.1)

        deadline = time.monotonic() + time_limit
        correct = 0
        for expected in sequence:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            def show_sequence_progress(seconds_left):
                _render_minigame_panel(
                    title,
                    [
                        ("REPETÍ LA SECUENCIA", "yellow"),
                        (_minigame_bar(correct, count), "green"),
                        (f"MOVIMIENTOS {correct}/{count}", "white"),
                        (f"TIEMPO {seconds_left:0.1f} s", "red" if seconds_left < 2 else "cyan"),
                        (_minigame_bar(seconds_left, time_limit), "yellow"),
                    ],
                    accent="cyan",
                    footer="FLECHAS O W A S D",
                )

            pressed = _minigame_wait_key(fd, remaining, show_sequence_progress)
            if pressed != expected:
                break
            correct += 1

        success = correct == count
        _render_minigame_panel(
            "RUTA RECUPERADA" if success else "RUTA INTERRUMPIDA",
            [
                (f"{correct}/{count} movimientos correctos", "green" if success else "red"),
                ("BONIFICACIÓN ASEGURADA" if success else "SE CONSERVA EL RESULTADO BASE", "yellow"),
            ],
            accent="green" if success else "red",
        )
        time.sleep(0.8)
        return success


def _perimeter_reflex_game(rounds=4, time_limit=1.25):
    directions = tuple(ARENA_MOVES)
    correct = 0
    with _minigame_terminal() as fd:
        if fd is None:
            return 0

        for round_number in range(1, rounds + 1):
            target = random.choice(directions)
            round_limit = max(0.85, time_limit - (round_number - 1) * 0.08)

            def show_perimeter_signal(seconds_left):
                _render_minigame_panel(
                    "BRECHA EN EL PERÍMETRO",
                    [
                        (f"SEÑAL {round_number}/{rounds}", "yellow"),
                        (_direction_glyph(target), "red"),
                        (f"TIEMPO {seconds_left:.2f} s", "white"),
                        (_minigame_bar(correct, rounds), "green"),
                        (f"ACCESOS CUBIERTOS {correct}/{rounds}", "cyan"),
                    ],
                    accent="red",
                    footer="FLECHAS O W A S D",
                )

            pressed = _minigame_wait_key(fd, round_limit, show_perimeter_signal)
            if pressed == target:
                correct += 1
                feedback = "Acceso cubierto."
            elif not pressed:
                feedback = "Llegaste tarde."
            else:
                feedback = "Señal equivocada."
            _render_minigame_panel(
                "SEÑAL CUBIERTA" if pressed == target else "SEÑAL PERDIDA",
                [
                    (feedback, "green" if pressed == target else "red"),
                    (_minigame_bar(correct, rounds), "green"),
                    (f"ACCESOS {correct}/{rounds}", "yellow"),
                ],
                accent="green" if pressed == target else "red",
            )
            time.sleep(0.45)

        time.sleep(0.7)
        return correct


def _radio_cipher_game(length=4, time_limit=7.0):
    code = "".join(str(random.randrange(10)) for _ in range(length))
    answer = code[::-1]
    with _minigame_terminal() as fd:
        if fd is None:
            return False

        _render_minigame_panel(
            "INTERCEPTAR EL CÓDIGO DE RADIO",
            [
                ("MEMORIZÁ LA CLAVE", "yellow"),
                ("   ·   ".join(code), "magenta"),
                (f"{length} DÍGITOS  ·  RESPUESTA EN ORDEN INVERSO", "dim"),
            ],
            accent="magenta",
            footer="PREPARATE PARA INGRESAR LOS NÚMEROS",
        )
        time.sleep(1.4 + length * 0.1)

        deadline = time.monotonic() + time_limit
        entered = ""
        while len(entered) < length:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            def show_radio_progress(seconds_left):
                _render_minigame_panel(
                    "INTERCEPTAR EL CÓDIGO DE RADIO",
                    [
                        ("INGRESÁ LA CLAVE AL REVÉS", "yellow"),
                        (_minigame_bar(len(entered), length), "magenta"),
                        (f"DÍGITOS {len(entered)}/{length}", "white"),
                        (f"FRECUENCIA {seconds_left:0.1f} s", "red" if seconds_left < 2 else "cyan"),
                        (_minigame_bar(seconds_left, time_limit), "yellow"),
                    ],
                    accent="magenta",
                    footer="INGRESÁ LOS NÚMEROS SIN ENTER",
                )

            pressed = _minigame_wait_key(fd, remaining, show_radio_progress)
            if len(pressed) != 1 or pressed not in "0123456789":
                break
            entered += pressed

        success = entered == answer
        _render_minigame_panel(
            "FRECUENCIA DECODIFICADA" if success else "SEÑAL PERDIDA",
            [
                (f"{len(entered)}/{length} dígitos ingresados", "green" if success else "red"),
                ("BONIFICACIÓN ASEGURADA" if success else "SE CONSERVA EL RESULTADO BASE", "yellow"),
            ],
            accent="green" if success else "red",
        )
        time.sleep(0.8)
        return success


HORDE_QTE_SCENES = (
    {
        "situation": (
            "La horda entra al patio. La escalera al techo está despejada; "
            "el callejón está lleno de caminantes."
        ),
        "safe": "Subir al techo y trabar la escotilla.",
        "unsafe": "Correr por el callejón hacia la calle.",
        "bonus": {"defense": 1},
        "bonus_label": "Defensas +1",
    },
    {
        "situation": (
            "Los golpes se acercan por el corredor. El cuarto de hormigón tiene "
            "una puerta sólida y ventilación cerrada."
        ),
        "safe": "Entrar en silencio y asegurar la puerta.",
        "unsafe": "Atravesar el corredor antes de que llegue la horda.",
        "bonus": {"intel": 1},
        "bonus_label": "Inteligencia +1",
    },
    {
        "situation": (
            "Una persona quedó separada. La horda mira al portón; la puerta "
            "lateral del depósito permite reunirse sin cruzar el patio."
        ),
        "safe": "Abrir la puerta lateral y trabarla tras reagruparse.",
        "unsafe": "Gritarle que corra por el patio hasta la salida.",
        "bonus": {"morale": 1},
        "bonus_label": "Moral +1",
    },
)
HORDE_QTE_TIME_LIMITS = (7.0, 6.0, 5.0)


def horde_quick_time_event(state=None):
    """Run three timed choices; state is omitted for a non-persistent test."""
    bonuses = []
    with _minigame_terminal() as fd:
        if fd is None:
            return {
                "completed": False,
                "cleared": 0,
                "bonuses": bonuses,
                "failure": "No se pudo leer una respuesta en la terminal.",
            }

        for index, scene in enumerate(HORDE_QTE_SCENES):
            time_limit = HORDE_QTE_TIME_LIMITS[index]
            correct_side = random.choice(("left", "right"))
            left_option, right_option = (
                (scene["safe"], scene["unsafe"])
                if correct_side == "left"
                else (scene["unsafe"], scene["safe"])
            )

            def show_horde_progress(seconds_left):
                _render_minigame_panel(
                    "HORDA EN EL CORREDOR",
                    [
                        (f"DECISIÓN {index + 1}/{len(HORDE_QTE_SCENES)}", "yellow"),
                        (scene["situation"], "white"),
                        (f"1 / ←  {left_option}", "cyan"),
                        (f"2 / →  {right_option}", "magenta"),
                        (f"TIEMPO {seconds_left:0.1f} s", "red" if seconds_left < 2 else "yellow"),
                        (_minigame_bar(seconds_left, time_limit, 16), "red" if seconds_left < 2 else "green"),
                    ],
                    accent="yellow",
                    footer="ELEGÍ 1 / 2 O ← / →",
                )

            pressed = _minigame_wait_key(
                fd,
                time_limit,
                show_horde_progress,
            )
            if pressed in ("1", "a"):
                selected_side = "left"
            elif pressed in ("2", "d"):
                selected_side = "right"
            else:
                selected_side = ""

            if selected_side != correct_side:
                if not pressed:
                    failure = "Se acabó el tiempo; la horda alcanzó al grupo en el corredor."
                else:
                    failure = "La decisión dejó expuesto al grupo y la horda alcanzó el corredor."
                _render_minigame_panel(
                    "LA HORDA ALCANZÓ EL REFUGIO",
                    [
                        (f"DECISIÓN {index + 1}/{len(HORDE_QTE_SCENES)} FALLIDA", "red"),
                        (failure, "white"),
                        (f"Etapas superadas: {index}/{len(HORDE_QTE_SCENES)}", "yellow"),
                        ("LA CAMPAÑA TERMINA", "red"),
                    ],
                    accent="red",
                )
                time.sleep(0.9)
                return {
                    "completed": False,
                    "cleared": index,
                    "bonuses": bonuses,
                    "failure": failure,
                }

            if state is not None:
                bonus = effect_summary(state, scene["bonus"])
                apply_changes(state, scene["bonus"])
            else:
                bonus = scene["bonus_label"]
            bonuses.append(bonus)
            _render_minigame_panel(
                "PASO SUPERADO",
                [
                    (f"DECISIÓN {index + 1}/{len(HORDE_QTE_SCENES)} CORRECTA", "green"),
                    (f"Bonificación: {bonus}", "yellow"),
                    (f"Pasos pendientes: {len(HORDE_QTE_SCENES) - index - 1}", "white"),
                ],
                accent="green",
            )
            time.sleep(0.65)

        _render_minigame_panel(
            "SALIDA DESPEJADA",
            [
                ("La cuadrilla se reagrupó y salió del corredor.", "white"),
                ("Bonificaciones: " + ", ".join(bonuses), "yellow"),
                ("LA CAMPAÑA CONTINÚA", "green"),
            ],
            accent="green",
        )
        time.sleep(0.9)
        return {
            "completed": True,
            "cleared": len(HORDE_QTE_SCENES),
            "bonuses": bonuses,
            "failure": "",
        }


def end_campaign_on_horde_failure(state, reason):
    state["status"] = "failed"
    state["ending"] = {
        "title": "EL REFUGIO CAE ANTE LA HORDA",
        "score": 0,
        "text": reason,
        "epilogue": (
            "El corredor quedó abierto cuando la horda alcanzó a la cuadrilla. "
            "Quienes seguían en el refugio se dispersaron antes de que Rick pudiera "
            "reunirlos en un punto seguro. El asentamiento se perdió y ya no hubo "
            "una defensa común que pudiera recuperarlo. Esta campaña alternativa "
            "termina con la retirada desordenada del grupo; es un desenlace de la "
            "simulación y no un hecho del cómic."
        ),
    }


def optional_campaign_minigame(state, phase, choice, outcome):
    choice_id = choice["id"]
    if phase == "war" and state.get("war_turn") == 4 and choice_id == "war_hold":
        if not confirm(
            "HORDA DE CAMINANTES",
            "La horda llegó al corredor. La prueba tiene tres decisiones con 7, 6 "
            "y 5 segundos para responder. Elegir mal o dejar vencer el tiempo termina "
            "la campaña. Cada acierto da una bonificación; si elegís No, la campaña "
            "sigue sin la prueba ni sus bonos.\n\n"
            "Controles: 1/2 o flechas izquierda/derecha.\n\n¿Entrar a la prueba?",
            14,
            0,
        ):
            return "\n\nSe evitó el evento de la horda; la campaña sigue sin bonificaciones extra."

        result = horde_quick_time_event(state)
        if result["completed"]:
            return (
                "\n\nMINIJUEGO HORDA: salida despejada; bonificaciones: "
                + ", ".join(result["bonuses"])
                + "."
            )

        end_campaign_on_horde_failure(state, result["failure"])
        return (
            "\n\nMINIJUEGO HORDA: "
            + result["failure"]
            + " FIN DE CAMPAÑA: el refugio cayó ante la horda."
        )

    if "\n\nÉXITO:" not in outcome:
        return ""

    if phase == "expedition" and choice_id in {
        "food_run", "water_run", "medicine_run", "infested_depot"
    }:
        title = "RASTREAR SUMINISTROS"
        game = "route"
        reward_by_choice = {
            "food_run": {"food": 2},
            "water_run": {"water": 2},
            "medicine_run": {"medicine": 1},
            "infested_depot": {"food": 1, "medicine": 1},
        }
        reward = {"resources": reward_by_choice[choice_id]}
        description = "La expedición encontró señales de una reserva adicional."
    elif phase == "preparation" and choice_id == "prep_scavenge":
        title = "RASTREAR SUMINISTROS"
        game = "route"
        reward = {"resources": {"food": 2, "water": 1}}
        description = "La cuadrilla vio otra ruta de acceso al depósito."
    elif phase == "crisis" and choice_id == "crisis_fortify":
        title = "BRECHA EN EL PERÍMETRO"
        game = "perimeter"
        reward = {}
        description = "La alarma detectó cuatro puntos de presión en el perímetro."
    elif phase == "war" and choice_id == "war_sabotage":
        title = "INTERCEPTAR EL CÓDIGO DE RADIO"
        game = "signal"
        reward = {"resources": {"materials": 1, "medicine": 1}}
        description = "El equipo interceptó una clave que puede revelar dónde guardan suministros."
    elif phase == "war" and choice_id == "war_supply":
        title = "RECUPERAR EL CONVOY"
        game = "route"
        reward = {"resources": {"food": 2, "water": 1}}
        description = "El convoy quedó localizado, pero hay que seguir sus señales."
    else:
        return ""

    if game == "perimeter":
        rounds = 4
        reaction_time = 1.25
        challenge_description = "Cuatro señales; el tiempo baja de 1,25 a 1,01 segundos por respuesta."
        reward_description = (
            "Con 3/4 aciertos: defensas +1. Con 4/4: además, materiales +1."
        )
    else:
        if game == "signal":
            war_turn = state.get("war_turn", 1)
            sequence_length = 4 + int(war_turn >= 4) + int(war_turn >= 7)
        elif phase == "preparation":
            sequence_length = 4 + int(state.get("preparation_turn", 1) >= 3)
        elif phase == "war":
            war_turn = state.get("war_turn", 1)
            sequence_length = 4 + int(war_turn >= 4) + int(war_turn >= 7)
        else:
            sequence_length = 4
        time_limit = 7.0 + (sequence_length - 4) * 0.8
        display_time = 1.4 + sequence_length * 0.1
        challenge_name = "dígitos al revés" if game == "signal" else "flechas"
        challenge_description = (
            f"Memorizá {sequence_length} {challenge_name} durante {display_time:.1f} s; "
            f"después tenés {time_limit:.1f} s para responder."
        )
        reward_description = f"Al completarlo: {effect_summary(state, reward)}."

    if not confirm(
        title,
        f"{description}\n\n{challenge_description}\n{reward_description}\n"
        "Si la omitís o fallás, conservás el resultado de la decisión.\n\n¿Intentarla?",
        14,
        0,
    ):
        return "\n\nSe omitió la prueba opcional; el resultado de la decisión se conserva."

    if game == "perimeter":
        score = _perimeter_reflex_game(rounds=rounds, time_limit=reaction_time)
        if score >= 3:
            apply_changes(state, {"defense": 1})
            bonus = "La guardia cubrió los accesos: defensas +1."
            if score == 4:
                apply_changes(state, {"resources": {"materials": 1}})
                bonus += " Materiales +1 por una reparación rápida."
        else:
            bonus = "La defensa mantuvo el perímetro, pero no se consiguió una mejora extra."
        return f"\n\nMINIJUEGO ({score}/4): {bonus}"

    if game == "signal":
        succeeded = _radio_cipher_game(
            length=sequence_length,
            time_limit=time_limit,
        )
    else:
        succeeded = _direction_sequence_game(
            title,
            count=sequence_length,
            time_limit=time_limit,
        )

    if succeeded:
        reward_text = effect_summary(state, reward)
        apply_changes(state, reward)
        result_label = "código decodificado" if game == "signal" else "ruta completada"
        return f"\n\nMINIJUEGO: {result_label}; {reward_text}."
    return "\n\nMINIJUEGO: no se completó la prueba; se conserva el resultado de la decisión."


def _arena_speed_factor(elapsed):
    return max(
        ARENA_MIN_SPEED_FACTOR,
        1.0 - max(0.0, elapsed) * ARENA_SPEEDUP_PER_SECOND,
    )


def _arena_walkable(position):
    x, y = position
    return (
        0 <= x < ARENA_WIDTH
        and 0 <= y < ARENA_HEIGHT
        and position not in ARENA_WALLS
    )


def _arena_distances(target, blocked):
    distances = {target: 0}
    queue = [target]
    index = 0
    while index < len(queue):
        x, y = queue[index]
        index += 1
        for dx, dy in ARENA_MOVES.values():
            neighbor = (x + dx, y + dy)
            if (
                neighbor in distances
                or not _arena_walkable(neighbor)
                or (neighbor in blocked and neighbor != target)
            ):
                continue
            distances[neighbor] = distances[(x, y)] + 1
            queue.append(neighbor)
    return distances


def _arena_far_spawn(player, enemies, skip=None):
    occupied = {
        enemy["position"] for enemy in enemies if enemy is not skip
    }
    distances = _arena_distances(player, occupied)
    candidates = [
        position for position in ARENA_SPAWNS
        if position not in occupied and position in distances
    ]
    if not candidates:
        candidates = [
            (x, y)
            for y in range(ARENA_HEIGHT)
            for x in range(ARENA_WIDTH)
            if _arena_walkable((x, y))
            and (x, y) not in occupied
            and (x, y) in distances
        ]
    farthest = max(distances[position] for position in candidates)
    return random.choice(
        [position for position in candidates if distances[position] == farthest]
    )


def _arena_spawn_enemy(symbol, player, enemies, now, elapsed=0.0):
    base_interval = {"S": 0.46, "N": 0.54, "Z": 0.62}[symbol]
    interval = base_interval * _arena_speed_factor(elapsed)
    return {
        "symbol": symbol,
        "position": _arena_far_spawn(player, enemies),
        "warning": None,
        "base_interval": base_interval,
        "interval": interval,
        "next_move": now + random.uniform(0.25, interval),
    }


def _arena_update_enemies(player, enemies, now, elapsed):
    hits = 0
    for enemy in enemies:
        enemy["interval"] = enemy["base_interval"] * _arena_speed_factor(elapsed)
        if now < enemy["next_move"]:
            continue
        enemy["next_move"] = now + enemy["interval"]

        if enemy["warning"] == player:
            hits += 1
            enemy["warning"] = None
            enemy["position"] = _arena_far_spawn(player, enemies, skip=enemy)
            continue

        enemy["warning"] = None
        occupied = {
            other["position"] for other in enemies if other is not enemy
        }
        distances = _arena_distances(player, occupied)
        distance = distances.get(enemy["position"])
        if distance is None:
            continue
        if distance <= 1:
            enemy["warning"] = player
            continue

        x, y = enemy["position"]
        options = [
            (x + dx, y + dy)
            for dx, dy in ARENA_MOVES.values()
            if _arena_walkable((x + dx, y + dy))
            and (x + dx, y + dy) not in occupied
            and (x + dx, y + dy) in distances
        ]
        if options:
            best_distance = min(distances[position] for position in options)
            enemy["position"] = random.choice(
                [
                    position for position in options
                    if distances[position] == best_distance
                ]
            )
    return hits


def _arena_draw(player, enemies, seconds_left, lives, dodges, wave, event):
    enemy_tiles = {
        enemy["position"]: (
            "!" if enemy["warning"] == player else enemy["symbol"]
        )
        for enemy in enemies
    }
    columns, terminal_rows = shutil.get_terminal_size(fallback=(80, 24))
    title = "ALEXANDRIA // THE REFUGE"
    timer_color = "green" if seconds_left > 20 else "yellow" if seconds_left > 8 else "red"
    status = (
        f"OLEADA {wave}/{ARENA_WAVES}  TIEMPO {seconds_left:04.1f}s "
        f"{_minigame_bar(seconds_left, ARENA_DURATION, 12)}  "
        f"VIDAS {lives}/{ARENA_LIVES}  ESQUIVAS {dodges}  "
        f"BONUS +{min(6, dodges * 2)}"
    )
    legend = "@ vos  S Salvador  N Negan  Z caminante  ! ataque  # cobertura"
    panel_width = min(
        columns - 4,
        max(ARENA_WIDTH + 6, len(status) + 6, len(legend) + 6, len(title) + 6),
    )
    body_width = panel_width - 6
    frame = "╔" + "═" * (panel_width - 2) + "╗"
    frame_bottom = "╚" + "═" * (panel_width - 2) + "╝"
    lines = []

    def add_centered(plain, styled=None, color="white", bold=False):
        wrapped = textwrap.wrap(plain, width=body_width, break_long_words=True) or [""]
        for segment in wrapped:
            padding = max(0, (body_width - len(segment)) // 2)
            trailing = max(0, body_width - len(segment) - padding)
            plain_row = "║  " + " " * padding + segment + " " * trailing + "  ║"
            if styled is None or len(wrapped) > 1:
                styled_segment = _minigame_color(segment, color, bold)
            else:
                styled_segment = styled
            styled_row = "║  " + " " * padding + styled_segment + " " * trailing + "  ║"
            lines.append((plain_row, styled_row))

    lines.append((frame, _minigame_color(frame, "cyan", True)))
    add_centered(title, color="cyan", bold=True)
    add_centered(status, color=timer_color, bold=True)
    add_centered(legend, color="dim")
    border = "+" + "-" * ARENA_WIDTH + "+"
    add_centered(border, color="cyan")
    for y in range(ARENA_HEIGHT):
        row = []
        colored_row = []
        for x in range(ARENA_WIDTH):
            position = (x, y)
            if position == player:
                tile, color = "@", "cyan"
            elif position in enemy_tiles:
                tile = enemy_tiles[position]
                color = "red" if tile == "!" or tile == "N" else "yellow" if tile == "S" else "green"
            elif position in ARENA_WALLS:
                tile, color = "#", "white"
            else:
                tile, color = ".", "dim"
            row.append(tile)
            colored_row.append(_minigame_color(tile, color, tile in ("@", "!", "N")))
        plain_map_row = "|" + "".join(row) + "|"
        colored_map_row = "|" + "".join(colored_row) + "|"
        add_centered(plain_map_row, styled=colored_map_row)
    add_centered(border, color="cyan")
    event_color = "red" if "alcanzaron" in event or "horda" in event else "yellow" if "Oleada" in event else "green" if "Esquiva" in event or "Resististe" in event else "white"
    add_centered(event, color=event_color, bold=True)
    add_centered("FLECHAS / W A S D MOVER  ·  Q TERMINA", color="cyan")
    lines.append((frame_bottom, _minigame_color(frame_bottom, "cyan", True)))

    visible_width = max(len(plain) for plain, _ in lines)
    top = max(0, (terminal_rows - len(lines)) // 2)
    left = max(0, (columns - visible_width) // 2)
    output = ["\x1b[H\x1b[J", "\n" * top]
    for index, (plain, styled) in enumerate(lines):
        padding = max(0, (visible_width - len(plain)) // 2)
        trailing = max(0, visible_width - len(plain) - padding)
        line = " " * (left + padding) + styled + " " * trailing
        if index < len(lines) - 1:
            line += "\n"
        output.append(line)
    sys.stdout.write("".join(output))
    sys.stdout.flush()


def quick_time_event():
    duration = ARENA_DURATION
    if not sys.stdin.isatty():
        return 0

    fd = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(fd)
    player = (ARENA_WIDTH // 2, ARENA_HEIGHT // 2)
    enemies = []
    started = time.monotonic()
    for symbol in ("S", "S", "Z"):
        enemies.append(_arena_spawn_enemy(symbol, player, enemies, started))

    spawn_schedule = ARENA_SPAWN_SCHEDULE
    next_spawn = 0
    lives = ARENA_LIVES
    dodges = 0
    last_move = 0.0
    next_frame = 0.0
    event = "Esquiva los ataques. Cuando aparezca !, movete antes de que impacte."
    finished_by_player = False

    try:
        tty.setcbreak(fd)
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()
        quiet_settings = termios.tcgetattr(fd)
        quiet_settings[3] &= ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSADRAIN, quiet_settings)

        while select.select([fd], [], [], 0)[0]:
            os.read(fd, 1)

        while lives > 0:
            now = time.monotonic()
            elapsed = now - started
            if elapsed >= duration:
                break

            while next_spawn < len(spawn_schedule) and elapsed >= spawn_schedule[next_spawn][0]:
                symbol = spawn_schedule[next_spawn][1]
                enemies.append(_arena_spawn_enemy(symbol, player, enemies, now, elapsed))
                event = f"¡Oleada nueva! Se acerca {'Negan' if symbol == 'N' else 'un caminante'}."
                next_spawn += 1

            wave = min(ARENA_WAVES, int(elapsed // (duration / ARENA_WAVES)) + 1)
            if now >= next_frame:
                _arena_draw(
                    player, enemies, max(0.0, duration - elapsed),
                    lives, dodges, wave, event,
                )
                next_frame = now + 0.10

            wake_at = min(
                started + duration,
                next_frame,
                min(enemy["next_move"] for enemy in enemies),
            )
            timeout = max(0.0, wake_at - time.monotonic())
            ready, _, _ = select.select([fd], [], [], timeout)
            if ready:
                pressed = _arena_read_key(fd)
                now = time.monotonic()
                if pressed == "q":
                    finished_by_player = True
                    break
                if pressed in ARENA_MOVES and now - last_move >= 0.10:
                    dx, dy = ARENA_MOVES[pressed]
                    destination = (player[0] + dx, player[1] + dy)
                    occupied = {enemy["position"] for enemy in enemies}
                    if not _arena_walkable(destination):
                        event = "La cobertura bloquea el paso."
                    elif destination in occupied:
                        event = "Un enemigo te cierra el paso."
                    else:
                        old_position = player
                        player = destination
                        escaped = 0
                        for enemy in enemies:
                            if enemy["warning"] == old_position:
                                enemy["warning"] = None
                                escaped += 1
                        if escaped:
                            dodges += escaped
                            event = f"¡Esquiva! Evitaste {escaped} ataque(s)."
                        else:
                            event = "Seguí moviéndote; los enemigos se acercan."
                    last_move = now

            now = time.monotonic()
            elapsed = now - started
            while next_spawn < len(spawn_schedule) and elapsed >= spawn_schedule[next_spawn][0]:
                symbol = spawn_schedule[next_spawn][1]
                enemies.append(_arena_spawn_enemy(symbol, player, enemies, now, elapsed))
                event = f"¡Oleada nueva! Se acerca {'Negan' if symbol == 'N' else 'un caminante'}."
                next_spawn += 1

            hits = _arena_update_enemies(player, enemies, now, elapsed)
            if hits:
                lives = max(0, lives - hits)
                event = f"¡Te alcanzaron {hits} vez/veces! Perdés vida y el enemigo vuelve a aparecer."

        elapsed = min(duration, time.monotonic() - started)
        wave = min(ARENA_WAVES, int(elapsed // (duration / ARENA_WAVES)) + 1)
        if lives <= 0:
            event = "La horda te alcanzó. El desenlace continúa con las esquivas logradas."
        elif finished_by_player:
            event = "Terminaste la prueba; el desenlace continúa con las esquivas logradas."
        else:
            event = "¡Resististe la oleada completa de 40 segundos!"
        _arena_draw(
            player, enemies, max(0.0, duration - elapsed),
            lives, dodges, wave, event,
        )
        time.sleep(0.65)
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, previous_settings)
        finally:
            sys.stdout.write("\x1b[?25h\x1b[2J\x1b[H")
            sys.stdout.flush()

    return dodges


def decide_ending(state, final_choice, reflex_dodges=0):
    bonus = min(6, max(0, reflex_dodges) * 2)
    if final_choice == "evacuate":
        title = "RETIRADA DEL REFUGIO"
        state["ending"] = {
            "title": title,
            "score": ending_score(state) + bonus,
            "text": "La comunidad abre una ruta de salida antes de quedar cercada. Se pierde el asentamiento, pero los supervivientes conservan la posibilidad de empezar de nuevo.",
            "epilogue": campaign_epilogue(state, title, final_choice),
        }
        return

    score = ending_score(state) + bonus
    if final_choice == "hold":
        if state["defense"] >= 4:
            score += 2
            result = "Las defensas permiten sostener el frente durante la confrontación."
        else:
            score -= 2
            result = "La defensa no estaba preparada para sostener el frente."
    else:
        if state["intel"] >= 2 or state["alliances"] >= 2:
            score += 3
            result = "La información y los contactos abren espacio para un acuerdo."
        else:
            score -= 2
            result = "Sin información ni aliados suficientes, la negociación queda debilitada."

    if score >= 35:
        title = "VICTORIA ESTRATÉGICA"
        text = "La defensa coordinada obliga a Negan a detener la ofensiva. La comunidad conserva recursos y margen para reconstruirse."
    elif score >= 27:
        title = "VICTORIA CON PÉRDIDAS"
        text = "El refugio resiste, pero el costo humano y material es alto. Los supervivientes tendrán que reconstruir sus defensas."
    elif score >= 20:
        title = "RETIRADA NEGOCIADA"
        text = "La comunidad evita quedar destruida, pero abandona terreno y suministros. El conflicto termina sin una victoria clara."
    else:
        title = "EL REFUGIO CAE"
        text = "La defensa no alcanza para sostener el asentamiento. Los supervivientes se dispersan y la campaña termina con la comunidad obligada a empezar de nuevo."
    state["ending"] = {
        "title": title,
        "score": score,
        "text": result + "\n\n" + text,
        "epilogue": campaign_epilogue(state, title, final_choice),
    }


def show_ending(state):
    ending = state.get("ending") if state else None
    if not ending:
        message("DESENLACE", "Todavía no hay un desenlace guardado.")
        return

    title = ending.get("title", "CAMPAÑA FINALIZADA")
    if not ending.get("epilogue"):
        final_choice = None
        decisions = state.get("decisions", [])
        if isinstance(decisions, list):
            for decision in reversed(decisions):
                if (
                    isinstance(decision, dict)
                    and decision.get("phase") == "Confrontación final"
                    and decision.get("choice") in {"hold", "talk", "evacuate"}
                ):
                    final_choice = decision["choice"]
                    break

        failure = ""
        if state.get("status") == "failed":
            failure = ending.get("text") or failure_reason(state)
        ending["epilogue"] = campaign_epilogue(
            state,
            title,
            final_choice=final_choice,
            failure=failure,
        )
        save_campaign(state)

    lines = [
        "THE REFUGE — LÍNEA ALTERNATIVA",
        f"DESENLACE: {title}",
        f"Puntaje estratégico: {ending.get('score', 0)}",
    ]
    if "reflex_dodges" in ending:
        lines.extend([
            f"Esquivas exitosas: {ending['reflex_dodges']}",
            f"Bonus de reflejos: +{ending.get('reflex_bonus', 0)} puntos",
        ])
    lines.append("")

    def append_wrapped(text):
        for paragraph in text.split("\n\n"):
            if paragraph.strip():
                lines.extend(textwrap.fill(paragraph, width=72).splitlines())
            lines.append("")

    lines.append("RESULTADO")
    append_wrapped(ending.get("text", ""))
    lines.append("CRÓNICA DE ESTA PARTIDA")
    append_wrapped(ending["epilogue"])
    lines.append("Esta narración es una variación original del cómic y no modifica su canon.")

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="alexandria-ending-",
        suffix=".txt",
        delete=False,
    ) as temporary:
        temporary.write("\n".join(lines))
        file_name = temporary.name
    try:
        call_dialog(["--title", f"EPÍLOGO — {title}", "--textbox", file_name, "22", "78"])
    finally:
        Path(file_name).unlink(missing_ok=True)



def final_decision(state):
    labels = {
        "hold": "Sostener el frente",
        "talk": "Negociar con Negan",
        "evacuate": "Abrir ruta de evacuación",
    }
    options = []
    for tag, label in labels.items():
        decision = {"id": f"final_{tag}"}
        probability = decision_success_probability(state, decision)
        success_percent = int(round(probability * 100))
        failure_percent = 100 - success_percent
        stats_label = decision_stat_short_label(decision)
        options.append(
            (tag, f"{label} · {success_percent}/{failure_percent}% · {stats_label}")
        )

    while True:
        selected = choose(
            "CONFRONTACIÓN FINAL",
            "Elegí cómo responder. Cada cifra indica éxito/fallo; las abreviaturas nombran las estadísticas que influyen.",
            options,
            16,
            0,
            5,
        )
        if selected is None:
            return False
        if confirm(
            "ANTES DE LA PRUEBA FINAL",
            f"Elegiste: {labels[selected]}.\n\n"
            "Después de confirmar, empezará una prueba de reflejos.\n"
            "Movete con las flechas o con W, A, S y D. Q termina la prueba.\n\n"
            "Es una oleada de 40 segundos y tenés dos vidas. "
            "Llegan refuerzos cada 2,5 segundos y los enemigos aumentan levemente su velocidad con el paso del tiempo.\n\n"
            "¿Empezar la confrontación?",
            14,
            0,
        ):
            break

    final_choice = {"id": f"final_{selected}"}
    probability = decision_success_probability(state, final_choice)
    success_percent = int(round(probability * 100))
    failure_percent = 100 - success_percent
    effects = {
        "hold": (
            {"defense": 1},
            {"defense": -1, "morale": -1},
            "La coordinación sostiene la línea.",
            "La línea cede parcialmente y la comunidad pierde confianza.",
        ),
        "talk": (
            {"alliances": 1, "morale": 1},
            {"alliances": -1, "intel": -1},
            "La negociación consigue apoyo y renueva la confianza.",
            "Negan rechaza los términos y la comunidad pierde influencia.",
        ),
        "evacuate": (
            {"morale": 1},
            {"morale": -2, "defense": -1},
            "La ruta de salida se mantiene abierta.",
            "La ruta queda expuesta y la retirada se vuelve más difícil.",
        ),
    }
    success_changes, failure_changes, success_text, failure_text = effects[selected]
    if random.random() < probability:
        apply_changes(state, success_changes)
        decision_result = f"ÉXITO ({success_percent}%): {success_text}"
    else:
        apply_changes(state, failure_changes)
        decision_result = f"FALLO ({failure_percent}%): {failure_text}"

    reflex_dodges = quick_time_event()
    reflex_bonus = min(6, reflex_dodges * 2)
    state["status"] = "complete"
    decide_ending(state, selected, reflex_dodges)
    state["ending"]["text"] = decision_result + "\n\n" + state["ending"]["text"]
    record_decision(
        state,
        "Confrontación final",
        selected,
        f"{decision_result} — {state['ending']['title']}; "
        f"esquivas {reflex_dodges}, reflejos +{reflex_bonus}",
    )
    state["ending"]["reflex_dodges"] = reflex_dodges
    state["ending"]["reflex_bonus"] = reflex_bonus
    save_campaign(state)
    show_ending(state)
    return True


def play_campaign(state):
    while state["status"] == "active":
        phase = state["phase"]
        if phase == "final":
            if not final_decision(state):
                return
            return

        title, description = PHASES[phase]
        if phase == "war":
            title = f"GUERRA — TURNO {state['war_turn']} DE {WAR_TURNS}"
        elif phase == "preparation":
            title = (
                f"PREPARACIÓN — JORNADA "
                f"{state.get('preparation_turn', 1)} DE {PREPARATION_TURNS}"
            )

        prompt = (
            f"{description}\n\n"
            "Cada opción muestra éxito/fallo, la estadística y sus efectos. "
            "Abrev.: Sup., Intel., Def., Med., Mat., Com., Ag. y Al.\n\n"
            f"{status_text(state)}\n"
            f"{ration_forecast_text(state)}"
        )
        if phase == "war" and state.get("war_turn") == 4:
            prompt += (
                "\n\nEn este turno, elegir Mantener la línea abre una prueba "
                "opcional ante la horda. Tres decisiones cronometradas; un error "
                "termina la campaña."
            )
        raw_choices = choices_for(phase, state)
        choices = available(raw_choices, state)
        menu_choices = []
        for index, choice in enumerate(choices, start=1):
            success_percent = int(round(decision_success_probability(state, choice) * 100))
            failure_percent = 100 - success_percent
            item_description = (
                f"{choice['label']} · {success_percent}/{failure_percent}% · "
                f"{decision_stat_short_label(choice)} · {compact_choice_hint(choice)}"
            )
            menu_choices.append((str(index), item_description))
        selected = choose(title, prompt, menu_choices, 23, 0, 8)
        if selected is None:
            return

        choice = choices[int(selected) - 1]
        if choice.get("risk") and not confirm(
            "REVISÁ EL RIESGO",
            f"{risk_preview_text(state, choice)}\n\n¿Confirmar esta decisión?",
            20,
            0,
        ):
            continue

        outcome = resolve_choice(state, choice)
        failure = finish_if_failed(state)
        if not failure and state["status"] == "active":
            outcome += optional_campaign_minigame(state, phase, choice, outcome)
        if state["status"] == "failed" and not failure:
            failure = state.get("ending", {}).get("text", "La campaña terminó.")
        if failure:
            if "FIN DE CAMPAÑA:" not in outcome:
                outcome += "\n\nFIN DE CAMPAÑA: " + failure
        else:
            outcome += "\n" + consume_rations(state)
            incident = resolve_random_incident(state)
            if incident:
                outcome += "\n\n" + incident
            failure = finish_if_failed(state)
            if failure:
                outcome += "\n\nFIN DE CAMPAÑA: " + failure

        record_decision(state, phase_label(state), choice["label"], outcome)
        if state["status"] == "active":
            advance(state)
        save_campaign(state)
        if state["status"] == "failed":
            message(
                "FIN DE CAMPAÑA",
                f"{outcome}\n\nIniciá una nueva campaña para volver a intentarlo.",
                18,
                76,
            )
            show_ending(state)
            return
        message(
            "DECISIÓN REGISTRADA",
            f"{outcome}\n\n{status_text(state)}",
            18,
            76,
        )


def show_status(state):
    if not state:
        message("COMUNIDAD", "Todavía no hay una campaña guardada.")
        return
    text = status_text(state)
    if state.get("status") in ("complete", "failed") and state.get("ending"):
        text += f"\n\nEstado: campaña finalizada — {state['ending']['title']}"
    else:
        text += f"\n\nEtapa actual: {phase_label(state)}"
    message("ESTADO DEL REFUGIO", text, 16, 76)


def show_archive(state):
    if not state or not state.get("decisions"):
        message("ARCHIVO DE DECISIONES", "Todavía no hay decisiones registradas.")
        return
    lines = ["REGISTRO DE CAMPAÑA", ""]
    for item in state["decisions"]:
        lines.extend([
            f"Jornada {item['day']} — {item['phase']}",
            f"Decisión: {item['choice']}",
            item["outcome"],
            "",
        ])
    if state.get("ending"):
        lines.extend([
            f"DESENLACE: {state['ending']['title']}",
            f"Puntaje estratégico: {state['ending']['score']}",
        ])

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="alexandria-refuge-",
        suffix=".txt",
        delete=False,
    ) as temporary:
        temporary.write("\n".join(lines))
        file_name = temporary.name
    try:
        call_dialog(["--title", "ARCHIVO DE DECISIONES", "--textbox", file_name, "22", "78"])
    finally:
        Path(file_name).unlink(missing_ok=True)


def show_about():
    message(
        "¿QUÉ ES THE REFUGE?",
        "THE REFUGE es una campaña de supervivencia por turnos ambientada en una línea alternativa de The Walking Dead.\n\n"
        "Vas a tomar diez decisiones de preparación y ocho durante la guerra, además de elegir cómo afrontar la confrontación final. Cada jornada consume comida y agua; durante la guerra se gastan dos raciones de cada una por turno. Las reservas pueden obligarte a cambiar de plan. Cada decisión muestra sus probabilidades de éxito y fallo, junto con la estadística que influye; fallar puede costar recursos y poner en riesgo la campaña.\n\n"
        "Las expediciones, las crisis y algunas operaciones de guerra pueden abrir minijuegos opcionales para conseguir suministros o mejorar la defensa. En el turno 4, Mantener la línea puede abrir el QTE de la horda: tres decisiones rápidas; equivocarse o tardar termina la campaña. La advertencia permite rechazarlo antes de empezar. La prueba final de esquiva dura 40 segundos. La partida se guarda localmente para que puedas continuarla. Los desenlaces son variaciones originales: no modifican el canon del cómic.",
        19,
        78,
    )


def show_rules():
    message(
        "THE REFUGE — REGLAS",
        "Campaña persistente: cinco etapas iniciales, cinco jornadas de preparación, ocho turnos de guerra y confrontación final: 18 decisiones estratégicas antes del desenlace.\n\n"
        "Cada jornada consume comida y agua; durante los ocho turnos de guerra se consumen dos raciones de cada una. Dos jornadas consecutivas con faltantes causan una baja. Cada opción muestra su probabilidad de éxito/fallo y la estadística que usa; un valor más alto aumenta las chances. En las maniobras arriesgadas también influyen inteligencia y defensas. Si no quedan supervivientes o colapsan moral y defensas, la campaña termina.\n\n"
        "Durante la preparación podés reponer comida y agua, intercambiar suministros, fortalecer accesos o atender a los heridos. Algunas expediciones, crisis y operaciones de guerra ofrecen minijuegos opcionales: acertar suma recursos o preparación; fallar una de esas pruebas no quita lo que ya ganaste. En el turno 4, Mantener la línea puede iniciar el QTE de la horda: tres decisiones de 7, 6 y 5 segundos; un error o dejar vencer el tiempo termina la campaña. La advertencia permite rechazarlo.\n\n"
        "La partida se guarda localmente. Escape vuelve al menú y conserva el último estado guardado.\n\n"
        "En la prueba final, movete con las flechas o con W, A, S y D. Resistís una oleada de 40 segundos, con dos vidas; los refuerzos llegan cada 2,5 segundos y los enemigos aumentan levemente su velocidad con el paso del tiempo. Q termina la prueba.\n\n"
        "Marco temático: All-Out War, The Walking Dead #115-126. Esta campaña presenta una variación original, sin reproducir páginas ni diálogos del cómic.",
        22,
        78,
    )


def start_campaign(current):
    if current and current.get("status") == "active":
        if not confirm("NUEVA CAMPAÑA", "Hay una campaña en curso. ¿Querés reemplazarla?"):
            return
    elif current:
        if not confirm("NUEVA CAMPAÑA", "¿Iniciar una nueva campaña y reemplazar el registro anterior?"):
            return

    state = create_campaign()
    save_campaign(state)
    message(
        "THE REFUGE",
        "La campaña comienza. Tomá diez decisiones de preparación antes de la guerra, que dura ocho turnos. Cada jornada consume comida y agua; en la guerra se gastan dos raciones de cada una por turno. Las reservas van a definir qué prioridades podés sostener.\n\n"
        "Algunas maniobras tienen riesgo y se indican en el menú. Los eventos aleatorios pueden alterar tus recursos; una decisión extrema puede acabar con la campaña.",
        11,
        74,
    )
    play_campaign(state)


TEST_DIFFICULTIES = {
    "inicial": 4,
    "media": 5,
    "avanzada": 6,
}


def _show_standalone_test_result(title, lines, accent="green"):
    with _minigame_terminal() as fd:
        if fd is None:
            print("\n".join(lines))
            return
        _render_minigame_panel(
            title,
            [(line, "white") for line in lines],
            accent=accent,
            footer="PRESIONÁ CUALQUIER TECLA PARA VOLVER",
        )
        while not _minigame_wait_key(fd, 3600):
            pass


def run_standalone_minigame(name, difficulty="inicial"):
    if not sys.stdin.isatty():
        print("Abrí una terminal interactiva para probar los minijuegos.", file=sys.stderr)
        return 1

    if name in ("ruta", "radio"):
        if difficulty not in TEST_DIFFICULTIES:
            print("Dificultad inválida: elegí inicial, media o avanzada.", file=sys.stderr)
            return 2
        sequence_length = TEST_DIFFICULTIES[difficulty]
        time_limit = 7.0 + (sequence_length - 4) * 0.8
    elif name in ("brecha", "arena", "horda"):
        if difficulty != "inicial":
            print(f"El minijuego {name} no tiene niveles de dificultad.", file=sys.stderr)
            return 2
    else:
        print("Minijuego inválido: elegí ruta, brecha, radio o arena.", file=sys.stderr)
        return 2

    if name == "ruta":
        completed = _direction_sequence_game(
            "PRUEBA INDEPENDIENTE // RASTREAR SUMINISTROS",
            count=sequence_length,
            time_limit=time_limit,
        )
        result = "Ruta completada." if completed else "Ruta incompleta."
        _show_standalone_test_result(
            "RESULTADO DE RUTA",
            [result, "La prueba no leyó, cambió ni guardó la campaña."],
            "green" if completed else "yellow",
        )
    elif name == "brecha":
        score = _perimeter_reflex_game()
        if score >= 4:
            result = "En campaña: defensas +1 y materiales +1."
        elif score >= 3:
            result = "En campaña: defensas +1; sin materiales extra."
        else:
            result = "En campaña: sin bonificación adicional."
        _show_standalone_test_result(
            "RESULTADO DE LA BRECHA",
            [f"Aciertos: {score}/4.", result, "No se aplicaron cambios a la campaña."],
            "green" if score >= 3 else "yellow",
        )
    elif name == "radio":
        decoded = _radio_cipher_game(
            length=sequence_length,
            time_limit=time_limit,
        )
        result = "Clave decodificada." if decoded else "Clave no decodificada."
        _show_standalone_test_result(
            "RESULTADO DE RADIO",
            [result, "La prueba no leyó, cambió ni guardó la campaña."],
            "green" if decoded else "yellow",
        )
    elif name == "horda":
        result = horde_quick_time_event()
        if result["completed"]:
            lines = [
                f"Decisiones correctas: {result['cleared']}/{len(HORDE_QTE_SCENES)}.",
                "Bonificaciones simuladas: " + ", ".join(result["bonuses"]) + ".",
                "La prueba no leyó ni modificó la campaña guardada.",
            ]
            accent = "green"
        else:
            lines = [
                f"Decisiones correctas: {result['cleared']}/{len(HORDE_QTE_SCENES)}.",
                result["failure"],
                "En campaña, este error terminaría la partida.",
                "La prueba no leyó ni modificó la campaña guardada.",
            ]
            accent = "red"
        _show_standalone_test_result("RESULTADO DE LA HORDA", lines, accent)
    else:
        dodges = quick_time_event()
        _show_standalone_test_result(
            "RESULTADO DE LA ARENA",
            [f"Esquivas registradas: {dodges}.", "No se leyó ni se modificó la campaña guardada."],
            "cyan",
        )
    return 0


def standalone_minigame_menu():
    options = [
        ("ruta_inicial", "Rastrear suministros · inicial, 4 flechas"),
        ("ruta_media", "Rastrear suministros · media, 5 flechas"),
        ("ruta_avanzada", "Rastrear suministros · avanzada, 6 flechas"),
        ("brecha", "Brecha del perímetro · cuatro señales"),
        ("radio_inicial", "Código de radio · inicial, 4 dígitos"),
        ("radio_media", "Código de radio · media, 5 dígitos"),
        ("radio_avanzada", "Código de radio · avanzada, 6 dígitos"),
        ("horda", "Horda de caminantes · tres decisiones rápidas"),
        ("arena", "Arena final · 40 segundos"),
        ("volver", "Volver a la terminal"),
    ]
    tests = {
        "ruta_inicial": ("ruta", "inicial"),
        "ruta_media": ("ruta", "media"),
        "ruta_avanzada": ("ruta", "avanzada"),
        "brecha": ("brecha", "inicial"),
        "radio_inicial": ("radio", "inicial"),
        "radio_media": ("radio", "media"),
        "radio_avanzada": ("radio", "avanzada"),
        "horda": ("horda", "inicial"),
        "arena": ("arena", "inicial"),
    }
    while True:
        selected = choose(
            "BANCO DE PRUEBAS — THE REFUGE",
            "Elegí un minijuego. Estas pruebas son independientes y no usan la campaña guardada.",
            options,
            20,
            0,
            9,
        )
        if selected in (None, "volver"):
            return 0
        name, difficulty = tests[selected]
        result = run_standalone_minigame(name, difficulty)
        if result:
            return result


def main(arguments=None):
    if arguments is None:
        arguments = sys.argv[1:]

    if arguments == ["--probar-minijuegos"]:
        return standalone_minigame_menu()
    if arguments and arguments[0] == "--probar-minijuego":
        if len(arguments) not in (2, 3):
            print(
                "Uso: refugio --probar-minijuego ruta|brecha|radio|horda|arena [inicial|media|avanzada]",
                file=sys.stderr,
            )
            return 2
        name = arguments[1]
        difficulty = arguments[2] if len(arguments) == 3 else "inicial"
        return run_standalone_minigame(name, difficulty)
    if arguments:
        print(
            "Uso: refugio [--probar-minijuegos | --probar-minijuego ruta|brecha|radio|horda|arena [inicial|media|avanzada]]",
            file=sys.stderr,
        )
        return 2

    if not DIALOG:
        print("THE REFUGE necesita dialog. Instalalo como root con: su -c 'apt install dialog'")
        return 1

    while True:
        state = load_campaign()
        options = [
            ("about", "¿Qué es THE REFUGE?"),
            ("new", "Iniciar una campaña"),
            ("continue", "Continuar la campaña guardada"),
            ("ending", "Leer desenlace y epílogo"),
            ("status", "Estado del refugio"),
            ("archive", "Archivo de decisiones"),
            ("rules", "Reglas y marco"),
            ("back", "Volver al menú principal"),
        ]
        selected = choose(
            "THE REFUGE",
            "Una campaña de supervivencia, decisiones y reconstrucción.",
            options,
            20,
            76,
            8,
        )

        if selected in (None, "back"):
            return 0
        if selected == "about":
            show_about()
        elif selected == "new":
            start_campaign(state)
        elif selected == "continue":
            if state and state.get("status") == "active":
                play_campaign(state)
            elif state and state.get("status") in ("complete", "failed"):
                show_ending(state)
            else:
                message("SIN PARTIDA", "Todavía no hay una campaña para continuar.")
        elif selected == "ending":
            show_ending(state)
        elif selected == "status":
            show_status(state)
        elif selected == "archive":
            show_archive(state)
        elif selected == "rules":
            show_rules()


if __name__ == "__main__":
    raise SystemExit(main())
