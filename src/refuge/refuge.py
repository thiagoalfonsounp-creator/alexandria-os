#!/usr/bin/env python3
"""Campaña de supervivencia en terminal para Alexandria OS."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
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

PHASES = {
    "council": (
        "CONSEJO DEL REFUGIO",
        "La comunidad tiene un breve margen para prepararse. Elegí una prioridad.",
    ),
    "expedition": (
        "EXPEDICIÓN",
        "Un grupo puede salir a buscar suministros o información. Cada salida deja al refugio con menos manos.",
    ),
    "crisis": (
        "CRISIS EN EL PERÍMETRO",
        "Una amenaza se acerca mientras la comunidad aún se organiza. Tu respuesta afectará la preparación.",
    ),
    "war": (
        "GUERRA CONTRA LOS SALVADORES",
        "La ofensiva comienza. En cada turno elegí entre sostener defensas, reunir apoyo, reconocer posiciones o negociar.",
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
        "resources": {
            "food": 6,
            "water": 6,
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
    return state


def status_text(state):
    r = state["resources"]
    return (
        f"Jornada: {state['day']}\n"
        f"Supervivientes: {state['survivors']}\n"
        f"Comida: {r['food']}   Agua: {r['water']}\n"
        f"Medicinas: {r['medicine']}   Materiales: {r['materials']}\n"
        f"Moral: {state['morale']}/10   Defensas: {state['defense']}/6\n"
        f"Inteligencia: {state['intel']}/6   Alianzas: {state['alliances']}/5"
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


def consume_rations(state):
    shortages = []
    for resource, label in (("food", "comida"), ("water", "agua")):
        if state["resources"][resource] > 0:
            state["resources"][resource] -= 1
        else:
            state["morale"] = max(0, state["morale"] - 1)
            shortages.append(label)
    if shortages:
        return "La reserva de " + " y ".join(shortages) + " se agotó; la moral baja."
    return "Se consumió una ración de comida y agua."


def phase_label(state):
    phase = state["phase"]
    if phase == "war":
        return f"GUERRA — TURNO {state['war_turn']} DE 3"
    return PHASES.get(phase, ("THE REFUGE", ""))[0]


def advance(state):
    phase = state["phase"]
    if phase == "council":
        state["phase"] = "expedition"
    elif phase == "expedition":
        state["phase"] = "crisis"
    elif phase == "crisis":
        state["phase"] = "war"
        state["war_turn"] = 1
    elif phase == "war":
        if state["war_turn"] < 3:
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


def decide_ending(state, final_choice):
    if final_choice == "evacuate":
        state["ending"] = {
            "title": "RETIRADA DEL REFUGIO",
            "score": ending_score(state),
            "text": "La comunidad abre una ruta de salida antes de quedar cercada. Se pierde el asentamiento, pero los supervivientes conservan la posibilidad de empezar de nuevo.",
        }
        return

    score = ending_score(state)
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
    state["ending"] = {"title": title, "score": score, "text": result + "\n\n" + text}


def final_decision(state):
    options = [
        ("hold", "Sostener el frente", "Aprovecha las defensas acumuladas"),
        ("talk", "Negociar con Negan", "Depende de inteligencia y alianzas"),
        ("evacuate", "Abrir una ruta de evacuación", "Prioriza salvar a la comunidad"),
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

    state["status"] = "complete"
    decide_ending(state, selected)
    record_decision(state, "Confrontación final", selected, state["ending"]["title"])
    save_campaign(state)
    message(
        state["ending"]["title"],
        f"{state['ending']['text']}\n\nPuntaje estratégico: {state['ending']['score']}\n\nEste cierre es una variación de juego; no modifica el canon del cómic.",
        14,
        76,
    )
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
            title = f"GUERRA — TURNO {state['war_turn']} DE 3"

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
        apply_changes(state, choice["changes"])
        ration_result = consume_rations(state)
        outcome = choice["result"] + "\n" + ration_result
        record_decision(state, phase_label(state), choice["label"], outcome)
        advance(state)
        save_campaign(state)
        message(
            "DECISIÓN REGISTRADA",
            f"{outcome}\n\n{status_text(state)}",
            16,
            76,
        )


def show_status(state):
    if not state:
        message("COMUNIDAD", "Todavía no hay una campaña guardada.")
        return
    text = status_text(state)
    if state["status"] == "complete" and state.get("ending"):
        text += f"\n\nEstado: campaña finalizada — {state['ending']['title']}"
    else:
        text += f"\n\nEtapa actual: {phase_label(state)}"
    message("ESTADO DEL REFUGIO", text, 15, 72)


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
        "Campaña persistente: consejo, expedición, crisis, tres turnos de guerra y una decisión final.\n\n"
        "Las decisiones modifican comida, agua, medicinas, materiales, supervivientes, moral, defensas, inteligencia y alianzas. Las reservas de comida y agua se consumen al cerrar cada jornada.\n\n"
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
        "La campaña comienza. Prepará el refugio, administrá las reservas y decidí cómo responder a la amenaza de los Salvadores.\n\n"
        "Las acciones y sus consecuencias se guardan después de cada jornada.",
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
            ("status", "Estado del refugio"),
            ("archive", "Archivo de decisiones"),
            ("rules", "Reglas y marco"),
            ("back", "Volver al menú principal"),
        ]
        selected = choose(
            "THE REFUGE",
            "Una campaña de supervivencia, decisiones y reconstrucción.",
            options,
            18,
            72,
            7,
        )

        if selected in (None, "back"):
            return 0
        if selected == "new":
            start_campaign(state)
        elif selected == "continue":
            if state and state.get("status") == "active":
                play_campaign(state)
            elif state and state.get("status") == "complete":
                message("CAMPAÑA FINALIZADA", "La partida guardada ya tiene un desenlace. Iniciá una nueva campaña para volver a jugar.")
            else:
                message("SIN PARTIDA", "Todavía no hay una campaña para continuar.")
        elif selected == "status":
            show_status(state)
        elif selected == "archive":
            show_archive(state)
        elif selected == "rules":
            show_rules()


if __name__ == "__main__":
    raise SystemExit(main())
