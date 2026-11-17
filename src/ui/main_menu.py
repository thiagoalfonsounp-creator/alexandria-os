#!/usr/bin/env python3
"""Menú principal de Alexandria OS con el logo rasterizado por Chafa."""

import curses
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "0.6"
MENU = (
    ("THE WORLD", "Archivo del cómic"),
    ("THE COMIC ARCHIVE", "Biblioteca personal"),
    ("THE REFUGE", "Campaña de supervivencia"),
    ("CUADERNO DE CAMPO", "Notas locales"),
    ("MANUAL / AYUDA", "Navegación y comandos"),
    ("TERMINAL", "Volver a la consola"),
)
SGR = re.compile(r"\x1b\[([0-9;]*)m")


def terminal_size():
    size = shutil.get_terminal_size((80, 24))
    return size.columns, size.lines


def terminal_colors():
    try:
        curses.setupterm(term=os.environ.get("TERM"), fd=sys.stdout.fileno())
        colors = curses.tigetnum("colors")
    except (curses.error, OSError):
        colors = 16
    return 256 if colors >= 256 else 16 if colors >= 16 else 8


def render_logo(path, columns, rows, color_count):
    result = subprocess.run(
        [
            "chafa",
            "--format=symbols",
            f"--colors={color_count}",
            "--symbols=block",
            f"--size={columns}x{rows}",
            f"--view-size={columns}x{rows}",
            "--font-ratio=1/2",
            "--relative=off",
            "--align=top,left",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    lines = []
    line = []
    foreground, background = 7, 0
    position = 0
    for match in SGR.finditer(result.stdout):
        segment = result.stdout[position : match.start()]
        for char in segment:
            if char == "\r":
                continue
            if char == "\n":
                lines.append(line)
                line = []
            else:
                line.append((char, foreground, background))
        codes = [int(code) if code else 0 for code in match.group(1).split(";")]
        i = 0
        while i < len(codes):
            code = codes[i]
            if code == 0:
                foreground, background = 7, 0
            elif code == 39:
                foreground = 7
            elif code == 49:
                background = 0
            elif code in (38, 48) and i + 2 < len(codes) and codes[i + 1] == 5:
                if code == 38:
                    foreground = codes[i + 2]
                else:
                    background = codes[i + 2]
                i += 2
            elif 30 <= code <= 37:
                foreground = code - 30
            elif 40 <= code <= 47:
                background = code - 40
            elif 90 <= code <= 97:
                foreground = code - 90 + 8
            elif 100 <= code <= 107:
                background = code - 100 + 8
            i += 1
        position = match.end()
    for char in result.stdout[position:]:
        if char == "\r":
            continue
        if char == "\n":
            lines.append(line)
            line = []
        else:
            line.append((char, foreground, background))
    if line:
        lines.append(line)
    return lines


def put(stdscr, y, x, text, style=0, limit=None):
    height, width = stdscr.getmaxyx()
    if y < 0 or y >= height or x >= width:
        return
    text = text[: max(0, min(width - x - 1, limit if limit is not None else width))]
    try:
        stdscr.addstr(y, x, text, style)
    except curses.error:
        pass


def draw_frame(stdscr, x, width, height, muted):
    right = x + width - 1
    try:
        stdscr.attron(muted)
        stdscr.addch(0, x, curses.ACS_ULCORNER)
        stdscr.addch(0, right, curses.ACS_URCORNER)
        stdscr.addch(height - 1, x, curses.ACS_LLCORNER)
        stdscr.addch(height - 1, right, curses.ACS_LRCORNER)
        for col in range(x + 1, right):
            stdscr.addch(0, col, curses.ACS_HLINE)
            stdscr.addch(height - 1, col, curses.ACS_HLINE)
        for row in range(1, height - 1):
            stdscr.addch(row, x, curses.ACS_VLINE)
            stdscr.addch(row, right, curses.ACS_VLINE)
        stdscr.attroff(muted)
    except curses.error:
        pass


def show_menu(stdscr, art, logo_width):
    curses.curs_set(0)
    stdscr.keypad(True)
    try:
        curses.set_escdelay(25)
    except (AttributeError, curses.error):
        pass
    selected = 0
    height, width = stdscr.getmaxyx()
    logo_x = max(0, (logo_width - max((len(row) for row in art), default=0)) // 2)
    logo_y = max(0, (height - len(art)) // 2)
    color_pairs = {}
    next_pair = 1

    def pair_for(fg, bg):
        nonlocal next_pair
        key = (fg, bg)
        if key not in color_pairs:
            if next_pair >= curses.COLOR_PAIRS:
                return 0
            try:
                curses.init_pair(next_pair, fg, bg)
            except curses.error:
                return 0
            color_pairs[key] = next_pair
            next_pair += 1
        return color_pairs[key]

    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
        except curses.error:
            pass
    muted = curses.A_DIM
    red = curses.A_BOLD
    try:
        red_pair = pair_for(curses.COLOR_RED, curses.COLOR_BLACK) if curses.has_colors() else 0
        white_pair = pair_for(curses.COLOR_WHITE, curses.COLOR_BLACK) if curses.has_colors() else 0
        muted = curses.color_pair(white_pair) | curses.A_DIM
        red = curses.color_pair(red_pair) | curses.A_BOLD
    except curses.error:
        pass

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.erase()
        for row_index, row in enumerate(art):
            y = logo_y + row_index
            if y >= height:
                break
            for col_index, (char, fg, bg) in enumerate(row[:logo_width]):
                x = logo_x + col_index
                if x >= logo_width or x >= width:
                    break
                try:
                    pair = pair_for(fg, bg) if curses.has_colors() else 0
                    stdscr.addstr(y, x, char, curses.color_pair(pair))
                except curses.error:
                    pass

        panel_x = logo_width
        panel_width = width - panel_x
        draw_frame(stdscr, panel_x, panel_width, height, muted)
        put(stdscr, 1, panel_x + 2, f"ALEXANDRIA OS {VERSION}", red, panel_width - 4)
        try:
            stdscr.addch(2, panel_x, curses.ACS_LTEE)
            stdscr.addch(2, width - 1, curses.ACS_RTEE)
            for col in range(panel_x + 1, width - 1):
                stdscr.addch(2, col, curses.ACS_HLINE)
        except curses.error:
            pass
        put(stdscr, 3, panel_x + 2, "Elegí una sección", muted, panel_width - 4)

        first_item = 5
        for index, (label, _description) in enumerate(MENU):
            marker = ">" if index == selected else " "
            style = red if index == selected else curses.A_NORMAL
            put(stdscr, first_item + index, panel_x + 2, f"{marker} {index + 1}  {label}", style, panel_width - 4)
        detail_y = first_item + len(MENU) + 1
        if detail_y < height - 4:
            put(stdscr, detail_y, panel_x + 2, MENU[selected][1], muted, panel_width - 4)
        put(stdscr, height - 3, panel_x + 2, "↑/↓ mover · Enter abrir", muted, panel_width - 4)
        put(stdscr, height - 2, panel_x + 2, "Esc o Q: salir", muted, panel_width - 4)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            selected = (selected - 1) % len(MENU)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected = (selected + 1) % len(MENU)
        elif key in (10, 13, curses.KEY_ENTER):
            return selected + 1
        elif ord("1") <= key <= ord("6"):
            selected = key - ord("1")
        elif key in (27, ord("q"), ord("Q")):
            return 0
        elif key == curses.KEY_RESIZE:
            return -1


def main():
    if len(sys.argv) != 2:
        print("Uso: main_menu.py RUTA_DEL_LOGO", file=sys.stderr)
        return 2
    logo = Path(sys.argv[1])
    if not logo.is_file() or not os.access(logo, os.R_OK):
        print(f"No encuentro el logo de Alexandria OS en: {logo}", file=sys.stderr)
        return 2
    if not shutil.which("chafa"):
        print("Falta Chafa. Instalá el paquete chafa para mostrar el logo en la terminal.", file=sys.stderr)
        return 2

    while True:
        columns, rows = terminal_size()
        if columns < 80 or rows < 24:
            print("Ampliá la terminal a 80×24 como mínimo para ver el logo y el menú completos.", file=sys.stderr)
            return 2
        logo_width = columns // 2
        logo_height = min(logo_width // 2, rows - 2)
        try:
            art = render_logo(logo, logo_width, logo_height, terminal_colors())
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"No se pudo preparar el logo para la terminal: {error}", file=sys.stderr)
            return 2
        selection = curses.wrapper(show_menu, art, logo_width)
        if selection >= 0:
            return selection


if __name__ == "__main__":
    raise SystemExit(main())
