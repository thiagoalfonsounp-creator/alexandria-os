#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
export ALEXANDRIA_ROOT="${ALEXANDRIA_ROOT:-$PROJECT_ROOT}"
carpeta="$ALEXANDRIA_ROOT/imports/comics"

while true; do
    opcion=$(dialog --title "THE COMIC ARCHIVE" \
        --menu "Biblioteca personal" 15 70 4 \
        1 "Ver catálogo local" \
        2 "Cómo importar archivos" \
        3 "Leer tomo en PDF" \
        0 "Volver al menú principal" \
        3>&1 1>&2 2>&3)

    case "$opcion" in
        1)
            listado=$(find "$carpeta" -maxdepth 1 -type f \( -iname "*.pdf" -o -iname "*.cbz" \) -printf "%f\n" | sort)
            if [ -z "$listado" ]; then
                dialog --title "CATÁLOGO VACÍO" --msgbox "No hay archivos PDF o CBZ en $carpeta. Copiá allí los cómics de uso autorizado y volvé a abrir el catálogo." 9 72
            else
                temporal=$(mktemp)
                printf '%s\n' "$listado" > "$temporal"
                dialog --title "CATÁLOGO LOCAL" --textbox "$temporal" 20 72
                rm -f "$temporal"
            fi
            ;;
        2)
            dialog --title "IMPORTAR ARCHIVOS" --msgbox "Copiá en $carpeta los cómics PDF o CBZ que tengas derecho a usar. Después elegí Ver catálogo local." 9 72
            ;;
        3) bash "$PROJECT_ROOT/src/comic_archive/lector_pdf.sh" ;;
        0|"") break ;;
        *) break ;;
    esac
done
