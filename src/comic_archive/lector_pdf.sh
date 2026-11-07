#!/bin/bash

carpeta="$HOME/alexandria-os/imports/comics"
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

while true; do
    rm -f "$temporal"/pagina-*.jpg
    pdftoppm -f "$pagina" -l "$pagina" -scale-to 1200 -jpeg "$ruta_pdf" "$temporal/pagina" >/dev/null 2>&1
    imagen=$(find "$temporal" -maxdepth 1 -type f -name "pagina-*.jpg" -print -quit)

    if [ -z "$imagen" ]; then
        dialog --title "ERROR DE LECTURA" --msgbox "No pude convertir la página $pagina del PDF." 8 64
        break
    fi

    clear
    printf '\033[5;78H'
    chafa --format sixels --view-size 209x92 --size 209x90 --colors full --scale max --exact-size off --align center,left --relative on "$imagen"
    printf '\033[49;80H\033[2KPágina %d de %d | n: siguiente | p: anterior | q: salir' "$pagina" "$paginas"

    IFS= read -r -n 1 -s tecla
    case "$tecla" in
        n|N)
            if [ "$pagina" -lt "$paginas" ]; then
                pagina=$((pagina + 1))
            fi
            ;;
        p|P)
            if [ "$pagina" -gt 1 ]; then
                pagina=$((pagina - 1))
            fi
            ;;
        q|Q)
            break
            ;;
    esac
done

clear
