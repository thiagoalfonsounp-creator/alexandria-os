#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ALEXANDRIA_ROOT="${ALEXANDRIA_ROOT:-$PROJECT_ROOT}"
carpeta="$ALEXANDRIA_ROOT/imports/comics"
mapfile -t pdfs < <(find "$carpeta" -maxdepth 1 -type f -iname "*.pdf" -printf "%f\n" | sort -f)

if [ "${#pdfs[@]}" -eq 0 ]; then
    dialog --title "LECTOR PDF" --msgbox "No hay archivos PDF en $carpeta." 8 68
    exit 0
fi

opciones=()
for indice in "${!pdfs[@]}"; do
    opciones+=("$((indice + 1))" "${pdfs[$indice]}")
done
opciones+=("0" "Volver")

seleccion=$(dialog --title "THE COMIC ARCHIVE" \
    --menu "Elegí un PDF para leer" 18 72 10 \
    "${opciones[@]}" \
    3>&1 1>&2 2>&3)

if [ -z "$seleccion" ] || [ "$seleccion" = "0" ]; then
    exit 0
fi

ruta_pdf="$carpeta/${pdfs[$((seleccion - 1))]}"
paginas=$(pdfinfo "$ruta_pdf" 2>/dev/null | awk '/^Pages:/ {print $2; exit}')

if ! [[ "$paginas" =~ ^[0-9]+$ ]]; then
    dialog --title "ERROR DE LECTURA" --msgbox "No pude obtener la cantidad de páginas del PDF." 8 64
    exit 1
fi

temporal=$(mktemp -d)
trap 'rm -rf "$temporal"' EXIT
pagina=1
zoom=4
offset_x=0
offset_y=0
pagina_renderizada=0
zoom_renderizado=0
arte="$temporal/pagina-arte.txt"
vista="$temporal/pagina-vista.txt"

dimensiones_terminal=$(stty size 2>/dev/null || true)
read -r lineas_terminal columnas_terminal <<< "$dimensiones_terminal"
if ! [[ "$lineas_terminal" =~ ^[0-9]+$ && "$columnas_terminal" =~ ^[0-9]+$ ]]; then
    lineas_terminal=$(tput lines 2>/dev/null || true)
    columnas_terminal=$(tput cols 2>/dev/null || true)
fi
if ! [[ "$lineas_terminal" =~ ^[0-9]+$ ]] || (( lineas_terminal < 10 )); then
    lineas_terminal=24
fi
if ! [[ "$columnas_terminal" =~ ^[0-9]+$ ]] || (( columnas_terminal < 20 )); then
    columnas_terminal=80
fi

alto_vista=$((lineas_terminal - 2))
ancho_vista=$((columnas_terminal - 1))
if (( alto_vista < 5 )); then alto_vista=5; fi
if (( ancho_vista < 10 )); then ancho_vista=10; fi

# En la consola virtual local, preferí una imagen de píxeles reales. El modo
# framebuffer/DRM no funciona desde SSH ni desde pseudo-terminales /dev/pts/*.
terminal_actual=$(tty 2>/dev/null || true)
consola_local=0
if [[ "${TERM:-}" == "linux" && "$terminal_actual" =~ ^/dev/tty[0-9]+$ ]]; then
    consola_local=1
fi

modo_imagen=0
dispositivo_video_disponible=0
if (( consola_local )); then
    for dispositivo in /dev/fb[0-9]*; do
        if [[ -c "$dispositivo" && -r "$dispositivo" && -w "$dispositivo" ]]; then
            dispositivo_video_disponible=1
            break
        fi
    done
    if (( ! dispositivo_video_disponible )); then
        for dispositivo in /dev/dri/card[0-9]*; do
            if [[ -c "$dispositivo" && -r "$dispositivo" && -w "$dispositivo" ]]; then
                dispositivo_video_disponible=1
                break
            fi
        done
    fi
    if command -v fbi >/dev/null 2>&1 && command -v fbgs >/dev/null 2>&1 && \
        command -v gs >/dev/null 2>&1 && (( dispositivo_video_disponible )); then
        modo_imagen=1
        dialog --title "LECTURA EN CONSOLA LOCAL" --msgbox \
            "Se abrirá el tomo completo en blanco y negro, ajustado inicialmente a la pantalla.

Flechas: desplazarte por la página. Espacio o j: siguiente página. k: página anterior.

En el visor: + / - cambian el zoom; a vuelve a ajustar la página; número + g salta a una página; q vuelve a Alexandria." 14 74
    else
        detalle=""
        if ! command -v fbi >/dev/null 2>&1 || ! command -v fbgs >/dev/null 2>&1 || ! command -v gs >/dev/null 2>&1; then
            detalle="Faltan fbi/fbgs o Ghostscript. Instalalos desde Debian: su -c 'apt install fbi ghostscript'."
        elif (( ! dispositivo_video_disponible )); then
            detalle="No hay un dispositivo de vídeo local accesible (/dev/fbN o /dev/dri/cardN)."
        fi
        dialog --title "LECTOR DE IMAGEN NO DISPONIBLE" --msgbox \
            "Para leer cómodamente, este modo necesita fbi y acceso local de lectura/escritura a /dev/fbN o /dev/dri/cardN.

$detalle

No voy a abrir la vista ASCII porque no permite leer cómodamente la página. Revisá el requisito y volvé a entrar desde la consola local de Debian." 14 74
        exit 1
    fi
fi

if (( modo_imagen )); then
    fbgs -r 120 --autozoom "$ruta_pdf"
    resultado_fbgs=$?
    clear
    if (( resultado_fbgs != 0 )); then
        dialog --title "LECTOR DE CÓMIC" --msgbox \
            "No se pudo abrir el tomo con el visor local. Revisá fbi, Ghostscript y el acceso al dispositivo framebuffer/DRM." 8 74
    fi
    exit "$resultado_fbgs"
fi

if (( ! modo_imagen )) && ! command -v chafa >/dev/null 2>&1; then
    dialog --title "LECTOR PDF" --msgbox \
        "No está disponible un visor para esta sesión. Para la consola local se necesita fbi/fbgs, Ghostscript y acceso a framebuffer/DRM; para SSH se necesita chafa." 9 72
    exit 1
fi

while true; do
    if (( pagina_renderizada != pagina )); then
        rm -f "$temporal"/pagina-*.jpg
        pdftoppm -f "$pagina" -l "$pagina" -scale-to 2400 -jpeg \
            "$ruta_pdf" "$temporal/pagina" >/dev/null 2>&1
        imagen=$(find "$temporal" -maxdepth 1 -type f -name "pagina-*.jpg" -print -quit)

        if [ -z "$imagen" ]; then
            dialog --title "ERROR DE LECTURA" --msgbox "No pude convertir la página $pagina del PDF." 8 64
            break
        fi
        pagina_renderizada=$pagina
        zoom_renderizado=0
        offset_x=0
        offset_y=0
    fi

    if (( zoom_renderizado != zoom )); then
        ancho_canvas=$((ancho_vista * zoom))
        alto_canvas=$((alto_vista * zoom))
        if ! chafa --format symbols --symbols ascii --view-size "${ancho_canvas}x${alto_canvas}" \
            --size "${ancho_canvas}x${alto_canvas}" --colors none --scale max --exact-size off \
            --align center,top --relative off "$imagen" > "$arte"; then
            dialog --title "ERROR DE LECTURA" --msgbox "No pude representar esta página. Revisá que chafa esté instalado." 8 68
            break
        fi

        read -r arte_ancho arte_alto < <(awk 'length($0) > ancho { ancho = length($0) } END { print ancho + 0, NR + 0 }' "$arte")
        if ! [[ "$arte_ancho" =~ ^[0-9]+$ && "$arte_alto" =~ ^[0-9]+$ ]] || (( arte_ancho == 0 || arte_alto == 0 )); then
            dialog --title "ERROR DE LECTURA" --msgbox "La página se convirtió, pero no produjo una imagen visible." 8 68
            break
        fi

        max_x=$((arte_ancho - ancho_vista))
        max_y=$((arte_alto - alto_vista))
        if (( max_x < 0 )); then max_x=0; fi
        if (( max_y < 0 )); then max_y=0; fi
        if (( offset_x > max_x )); then offset_x=$max_x; fi
        if (( offset_y > max_y )); then offset_y=$max_y; fi
        zoom_renderizado=$zoom
    fi

    paso_x=$((ancho_vista - 4))
    paso_y=$((alto_vista - 2))
    if (( paso_x < 1 )); then paso_x=1; fi
    if (( paso_y < 1 )); then paso_y=1; fi
    sectores_x=$(((max_x + paso_x - 1) / paso_x + 1))
    sectores_y=$(((max_y + paso_y - 1) / paso_y + 1))
    sector_x=$((offset_x / paso_x + 1))
    sector_y=$((offset_y / paso_y + 1))
    if (( max_x > 0 && offset_x == max_x )); then sector_x=$sectores_x; fi
    if (( max_y > 0 && offset_y == max_y )); then sector_y=$sectores_y; fi

    awk -v x="$offset_x" -v y="$offset_y" -v w="$ancho_vista" -v h="$alto_vista" \
        'NR > y && NR <= y + h { printf "%-*s\n", w, substr($0, x + 1, w); filas++ } END { while (filas < h) { printf "%-*s\n", w, ""; filas++ } }' \
        "$arte" > "$vista"

    clear
    printf '\033[H'
    cat "$vista"
    printf '\033[%d;1H\033[2K' "$((lineas_terminal - 1))"
    printf 'Página %s/%s | Zoom %sx | Sector %s/%s, %s/%s' \
        "$pagina" "$paginas" "$zoom" "$sector_x" "$sectores_x" "$sector_y" "$sectores_y"
    printf '\033[%d;1H\033[2K' "$lineas_terminal"
    printf 'Flechas/WASD mover | +/- zoom | 0 ajustar | n/p página | q salir'

    IFS= read -r -n 1 -s tecla
    if [[ "$tecla" == $'\x1b' ]]; then
        secuencia=""
        IFS= read -r -n 2 -s -t 0.15 secuencia || true
        case "$secuencia" in
            "[A"|OA) tecla=w ;;
            "[B"|OB) tecla=s ;;
            "[C"|OC) tecla=d ;;
            "[D"|OD) tecla=a ;;
            *) break ;;
        esac
    fi

    case "$tecla" in
        n|N)
            if (( pagina < paginas )); then pagina=$((pagina + 1)); fi
            ;;
        p|P)
            if (( pagina > 1 )); then pagina=$((pagina - 1)); fi
            ;;
        w|W)
            offset_y=$((offset_y - paso_y))
            if (( offset_y < 0 )); then offset_y=0; fi
            ;;
        s|S)
            offset_y=$((offset_y + paso_y))
            if (( offset_y > max_y )); then offset_y=$max_y; fi
            ;;
        a|A)
            offset_x=$((offset_x - paso_x))
            if (( offset_x < 0 )); then offset_x=0; fi
            ;;
        d|D)
            offset_x=$((offset_x + paso_x))
            if (( offset_x > max_x )); then offset_x=$max_x; fi
            ;;
        +|=)
            if (( zoom < 8 )); then
                zoom_anterior=$zoom
                zoom=$((zoom + 1))
                zoom_renderizado=0
                offset_x=$((offset_x * zoom / zoom_anterior))
                offset_y=$((offset_y * zoom / zoom_anterior))
            fi
            ;;
        -)
            if (( zoom > 1 )); then
                zoom_anterior=$zoom
                zoom=$((zoom - 1))
                zoom_renderizado=0
                offset_x=$((offset_x * zoom / zoom_anterior))
                offset_y=$((offset_y * zoom / zoom_anterior))
            fi
            ;;
        0)
            zoom=1
            zoom_renderizado=0
            offset_x=0
            offset_y=0
            ;;
        q|Q)
            break
            ;;
    esac
done

clear
