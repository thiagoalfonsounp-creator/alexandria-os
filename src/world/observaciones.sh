#!/usr/bin/env bash

DATA_DIR="$HOME/alexandria-os/data/world/field_observations"

mostrar_observacion() {
    local archivo="$1"
    local titulo="$2"

    if [[ -f "$archivo" ]]; then
        dialog --title "$titulo" --textbox "$archivo" 28 110
    else
        dialog --title "FIELD OBSERVATIONS" \
            --msgbox "No se encontró el registro seleccionado." 7 64
    fi
}

while true; do
    observacion=$(dialog --title "FIELD OBSERVATIONS" \
        --menu "Elegí una observación de campo" 16 82 6 \
        "FO-001" "Camuflaje por olor | The Walking Dead #4" \
        "FO-002" "Lurker durante una pausa | The Walking Dead #20" \
        "FO-003" "Presión de una horda | The Walking Dead #60" \
        "Volver" "Regresar a THE WORLD" \
        3>&1 1>&2 2>&3)

    case "$observacion" in
        "FO-001")
            mostrar_observacion "$DATA_DIR/fo_001.txt" "FIELD OBSERVATIONS | FO-001"
            ;;
        "FO-002")
            mostrar_observacion "$DATA_DIR/fo_002.txt" "FIELD OBSERVATIONS | FO-002"
            ;;
        "FO-003")
            mostrar_observacion "$DATA_DIR/fo_003.txt" "FIELD OBSERVATIONS | FO-003"
            ;;
        "Volver"|"")
            break
            ;;
    esac
done
