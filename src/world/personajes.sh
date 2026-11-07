#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="$PROJECT_ROOT/data/world"
INDEX_FILE="$DATA_DIR/personajes_index.tsv"

if [[ ! -r "$INDEX_FILE" ]]; then
    dialog --title "ARCHIVO DE PERSONAJES" \
        --msgbox "No se encontró el índice de personajes:\n$INDEX_FILE" 8 72
    exit 1
fi

declare -A archivo_por_personaje
opciones=()

while IFS=$'\t' read -r personaje grupo tipo nivel archivo; do
    [[ "$personaje" == "PERSONAJE" || -z "$personaje" || -z "$archivo" ]] && continue

    case "$nivel" in
        AMPLIADO) estado="Expediente ampliado" ;;
        BREVE) estado="Ficha breve" ;;
        IDENTIFICACIÓN)
            if [[ "$tipo" == "CAMINANTE" ]]; then
                estado="Caminante identificado"
            else
                estado="Animal identificado"
            fi
            ;;
        *) estado="Ficha" ;;
    esac

    opciones+=("$personaje" "$estado · $grupo")
    archivo_por_personaje["$personaje"]="$archivo"
done < "$INDEX_FILE"

if (( ${#opciones[@]} == 0 )); then
    dialog --title "ARCHIVO DE PERSONAJES" \
        --msgbox "El índice no contiene expedientes." 7 56
    exit 1
fi

while true; do
    personaje=$(dialog --title "ARCHIVO DE PERSONAJES" \
        --menu "Elegí qué expediente querés consultar" 28 110 14 \
        "${opciones[@]}" \
        "Volver" "Regresar a THE WORLD" \
        3>&1 1>&2 2>&3)
    estado_dialog=$?

    if (( estado_dialog != 0 )) || [[ "$personaje" == "Volver" ]]; then
        break
    fi

    archivo="${archivo_por_personaje[$personaje]:-}"
    if [[ -z "$archivo" || ! -r "$PROJECT_ROOT/$archivo" ]]; then
        dialog --title "ARCHIVO DE PERSONAJES" \
            --msgbox "No se puede abrir la ficha de $personaje." 7 58
        continue
    fi

    dialog --title "FICHA: $personaje" \
        --textbox "$PROJECT_ROOT/$archivo" 28 110
done
