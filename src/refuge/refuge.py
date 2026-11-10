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
        state["ending"] = {
            "title": "RETIRADA DEL REFUGIO",
            "score": ending_score(state) + bonus,
            "text": "La comunidad abre una ruta de salida antes de quedar cercada. Se pierde el asentamiento, pero los supervivientes conservan la posibilidad de empezar de nuevo.",
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
    state["ending"] = {"title": title, "score": score, "text": result + "\n\n" + text}


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
    save_campaign(state)
    message(
        state["ending"]["title"],
        f"{state['ending']['text']}\n\nEsquivas exitosas: {reflex_dodges}\n"
        f"Bonus de reflejos: +{reflex_bonus} puntos\n"
        f"Puntaje estratégico: {state['ending']['score']}\n\n"
        "Este cierre es una variación de juego; no modifica el canon del cómic.",
        16,
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
