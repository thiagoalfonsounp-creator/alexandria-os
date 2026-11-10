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
from pathlib import Path

DIALOG = shutil.which("dialog")
STATE_HOME = os.environ.get("XDG_STATE_HOME")
STATE_ROOT = Path(STATE_HOME) if STATE_HOME else Path.home() / ".local" / "state"
SAVE_FILE = STATE_ROOT / "alexandria-os" / "the-refuge.json"
SAVE_VERSION = 1

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

WAR_TURNS = 5
INCIDENT_CHANCE = 0.38

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
    "war": (
        "GUERRA CONTRA LOS SALVADORES",
        "La ofensiva avanza por cinco turnos. Cada decisión afecta los recursos y la capacidad de resistir.",
    ),
    "final": (
        "CONFRONTACIÓN FINAL",
        "Rick queda frente a Negan. La decisión final depende de la preparación acumulada y abre un desenlace alternativo.",
    ),
}


def call_dialog(args):
    if not DIALOG:
        print("No se encontró dialog. Instalalo con: sudo apt install dialog")
        raise SystemExit(1)
    return subprocess.run(
        [DIALOG, "--clear", "--stdout", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def message(title, text, height=12, width=76):
    call_dialog(["--title", title, "--msgbox", text, str(height), str(width)])


def confirm(title, text):
    result = call_dialog(["--title", title, "--yesno", text, "9", "68"])
    return result.returncode == 0


def choose(title, prompt, choices, height=20, width=78, menu_height=10):
    if not choices:
        return None
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


def available(choices, state):
    result = []
    for choice in choices:
        requirements = choice.get("requires", {})
        if all(state["resources"].get(name, 0) >= amount for name, amount in requirements.items()):
            result.append(choice)
    return result


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
                "label": "Infiltrarse en los suministros enemigos",
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
    apply_changes(state, choice.get("changes", {}))
    outcome = choice["result"]
    risk = choice.get("risk")
    if not risk:
        return outcome

    success_chance = (
        risk["success_chance"]
        + state["intel"] * risk.get("intel_bonus", 0)
        + state["defense"] * risk.get("defense_bonus", 0)
    )
    success_chance = max(0.05, min(0.95, success_chance))
    if random.random() < success_chance:
        apply_changes(state, risk.get("success_changes", {}))
        return outcome + "\n\nÉxito de la maniobra: " + risk["success_text"]

    apply_changes(state, risk.get("failure_changes", {}))
    return outcome + "\n\nFracaso de la maniobra: " + risk["failure_text"]


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
    for resource, label in (("food", "comida"), ("water", "agua")):
        if state["resources"][resource] > 0:
            state["resources"][resource] -= 1
        else:
            state["morale"] = max(0, state["morale"] - 1)
            shortages.append(label)

    if shortages:
        state["shortage_streak"] = state.get("shortage_streak", 0) + 1
    else:
        state["shortage_streak"] = 0

    result = "Se consumió una ración de comida y agua."
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


ARENA_WIDTH = 28
ARENA_HEIGHT = 9
ARENA_WALLS = {
    (7, 2), (8, 2), (7, 3), (8, 3),
    (13, 1), (14, 1), (13, 7), (14, 7),
    (19, 5), (20, 5), (19, 6), (20, 6),
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


def _arena_spawn_enemy(symbol, player, enemies, now):
    interval = {"S": 0.62, "N": 0.78, "Z": 0.86}[symbol]
    return {
        "symbol": symbol,
        "position": _arena_far_spawn(player, enemies),
        "warning": None,
        "interval": interval,
        "next_move": now + random.uniform(0.25, interval),
    }


def _arena_update_enemies(player, enemies, now):
    hits = 0
    for enemy in enemies:
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
    border = "+" + "-" * ARENA_WIDTH + "+"
    lines = [
        "THE REFUGE // PRUEBA DE ESQUIVA",
        (
            f"OLEADA {wave}/3  TIEMPO {seconds_left:04.1f}s  "
            f"VIDAS {lives}/3  ESQUIVAS {dodges}  "
            f"BONUS +{min(6, dodges * 2)}"
        ),
        "@ jugador | S Salvador | N Negan | Z caminante | ! ataque anunciado | # cobertura",
        border,
    ]
    for y in range(ARENA_HEIGHT):
        row = []
        for x in range(ARENA_WIDTH):
            position = (x, y)
            if position == player:
                row.append("@")
            elif position in enemy_tiles:
                row.append(enemy_tiles[position])
            elif position in ARENA_WALLS:
                row.append("#")
            else:
                row.append(".")
        lines.append("|" + "".join(row) + "|")
    lines.extend(
        [
            border,
            event,
            "W A S D mover | Q terminar la prueba | No hace falta presionar Enter",
        ]
    )
    sys.stdout.write("\x1b[H\x1b[J" + "\n".join(lines) + "\n")
    sys.stdout.flush()


def quick_time_event():
    duration = 18.0
    if not sys.stdin.isatty():
        return 0

    fd = sys.stdin.fileno()
    previous_settings = termios.tcgetattr(fd)
    player = (ARENA_WIDTH // 2, ARENA_HEIGHT // 2)
    enemies = []
    started = time.monotonic()
    for symbol in ("S", "S"):
        enemies.append(_arena_spawn_enemy(symbol, player, enemies, started))

    spawn_schedule = ((6.0, "N"), (12.0, "Z"))
    next_spawn = 0
    lives = 3
    dodges = 0
    last_move = 0.0
    next_frame = 0.0
    event = "Esquiva los ataques. Cuando aparezca !, movete antes de que impacte."
    finished_by_player = False

    try:
        tty.setcbreak(fd)
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
                enemies.append(_arena_spawn_enemy(symbol, player, enemies, now))
                event = f"¡Oleada nueva! Se acerca {'Negan' if symbol == 'N' else 'un caminante'}."
                next_spawn += 1

            wave = min(3, int(elapsed // 6) + 1)
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
                pressed = os.read(fd, 1).decode("ascii", errors="ignore").lower()
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
                enemies.append(_arena_spawn_enemy(symbol, player, enemies, now))
                event = f"¡Oleada nueva! Se acerca {'Negan' if symbol == 'N' else 'un caminante'}."
                next_spawn += 1

            hits = _arena_update_enemies(player, enemies, now)
            if hits:
                lives = max(0, lives - hits)
                event = f"¡Te alcanzaron {hits} vez/veces! Perdés vida y el enemigo vuelve a aparecer."

        elapsed = min(duration, time.monotonic() - started)
        wave = min(3, int(elapsed // 6) + 1)
        if lives <= 0:
            event = "La horda te alcanzó. El desenlace continúa con las esquivas logradas."
        elif finished_by_player:
            event = "Terminaste la prueba; el desenlace continúa con las esquivas logradas."
        else:
            event = "¡Resististe las tres oleadas!"
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
    epilogue = ending.get("epilogue") or (
        "Esta partida se guardó con una versión anterior del módulo y no incluye "
        "una crónica ampliada. Iniciá una campaña nueva para generar un epílogo."
    )
    append_wrapped(epilogue)
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
    options = [
        ("hold", "Sostener el frente — Aprovecha las defensas acumuladas"),
        ("talk", "Negociar con Negan — Depende de inteligencia y alianzas"),
        ("evacuate", "Abrir una ruta de evacuación — Prioriza salvar a la comunidad"),
    ]
    selected = choose(
        "CONFRONTACIÓN FINAL",
        "Elegí cómo responder. El desenlace pertenece a esta simulación alternativa.",
        options,
        16,
        76,
        5,
    )
    if selected is None:
        return False

    reflex_dodges = quick_time_event()
    reflex_bonus = min(6, reflex_dodges * 2)
    state["status"] = "complete"
    decide_ending(state, selected, reflex_dodges)
    record_decision(
        state,
        "Confrontación final",
        selected,
        f"{state['ending']['title']} — esquivas {reflex_dodges}, reflejos +{reflex_bonus}",
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

        prompt = f"{description}\n\n{status_text(state)}"
        raw_choices = choices_for(phase, state)
        choices = available(raw_choices, state)
        menu_choices = [
            (str(index), f"{choice['label']} — {choice['hint']}")
            for index, choice in enumerate(choices, start=1)
        ]
        selected = choose(title, prompt, menu_choices, 23, 86, 8)
        if selected is None:
            return

        choice = choices[int(selected) - 1]
        outcome = resolve_choice(state, choice)
        failure = finish_if_failed(state)
        if failure:
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


def show_rules():
    message(
        "THE REFUGE — REGLAS",
        "Campaña persistente: consejo, expedición, crisis, reconstrucción, refugiados, cinco turnos de guerra y confrontación final.\n\n"
        "Cada jornada consume comida y agua. Dos jornadas consecutivas con faltantes causan una baja. Los eventos aleatorios pueden ayudar o perjudicar; las maniobras arriesgadas dependen también de inteligencia y defensas. Si no quedan supervivientes o colapsan moral y defensas, la campaña termina.\n\n"
        "La partida se guarda localmente en formato JSON. Escape vuelve al menú y conserva el último estado guardado.\n\n"
        "Marco temático: All-Out War, The Walking Dead #115-126. Esta campaña presenta una variación original, sin reproducir páginas ni diálogos del cómic.",
        19,
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
        "La campaña comienza. Prepará el refugio durante diez jornadas antes de la confrontación final. La guerra ocupa cinco turnos.\n\n"
        "Algunas maniobras tienen riesgo y se indican en el menú. Los eventos aleatorios pueden alterar tus recursos; una decisión extrema puede acabar con la campaña.",
        11,
        74,
    )
    play_campaign(state)


def main():
    if not DIALOG:
        print("THE REFUGE necesita dialog. Instalalo con: sudo apt install dialog")
        return 1

    while True:
        state = load_campaign()
        options = [
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
        if selected == "new":
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
