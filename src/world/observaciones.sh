#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="$PROJECT_ROOT/data/world/field_observations"

mostrar_observacion() {
    local archivo="$1"
    local titulo="$2"
    local terminal_rows=24
    local terminal_cols=80
    local cuadro_alto
    local cuadro_ancho
    local ancho_texto
    local archivo_formateado
    local estado_dialog

    if [[ -r "$archivo" ]]; then
        read -r terminal_rows terminal_cols < <(
            stty size 2>/dev/null || printf '24 80\n'
        )

        cuadro_alto=$((terminal_rows - 4))
        cuadro_ancho=$((terminal_cols - 4))
        if ((cuadro_alto > 32)); then
            cuadro_alto=32
        fi
        if ((cuadro_ancho > 110)); then
            cuadro_ancho=110
        fi
        ancho_texto=$((cuadro_ancho - 4))
        archivo_formateado=$(mktemp) || return 1

        if ! fold -s -w "$ancho_texto" "$archivo" >"$archivo_formateado"; then
            rm -f -- "$archivo_formateado"
            dialog --title "FIELD OBSERVATIONS" \
                --msgbox "No se pudo preparar el registro para mostrarlo." 0 0
            return 1
        fi

        dialog --title "$titulo" --textbox "$archivo_formateado" \
            "$cuadro_alto" "$cuadro_ancho"
        estado_dialog=$?
        rm -f -- "$archivo_formateado"
        return "$estado_dialog"
    else
        dialog --title "FIELD OBSERVATIONS" \
            --msgbox "No se puede leer el registro seleccionado:\n$archivo" 0 0
    fi
}

while true; do
    observacion=$(dialog --title "FIELD OBSERVATIONS" \
        --menu "Elegí una observación de campo" 0 0 14 \
        "FO-001" "Camuflaje por olor | TWD #4" \
        "FO-002" "Lurker durante una pausa | TWD #20" \
        "FO-003" "Presión de una horda | TWD #60" \
        "FO-004" "Reanimación sin mordida | TWD #22" \
        "FO-005" "Amputación ante mordida | TWD #19" \
        "FO-006" "Inactividad por frío | TWD #21" \
        "FO-007" "Infiltración con pieles | TWD #132" \
        "FO-008" "Respuesta al fuego | TWD #14" \
        "FO-009" "Mutilación controlada | TWD #32" \
        "FO-010" "Degradación tisular | TWD #53" \
        "FO-011" "Propagación acústica | TWD #68" \
        "FO-012" "Armas contaminadas | TWD #159" \
        "FO-013" "Actividad en el agua | TWD #148" \
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
        "FO-004")
            mostrar_observacion "$DATA_DIR/fo_004.txt" "FIELD OBSERVATIONS | FO-004"
            ;;
        "FO-005")
            mostrar_observacion "$DATA_DIR/fo_005.txt" "FIELD OBSERVATIONS | FO-005"
            ;;
        "FO-006")
            mostrar_observacion "$DATA_DIR/fo_006.txt" "FIELD OBSERVATIONS | FO-006"
            ;;
        "FO-007")
            mostrar_observacion "$DATA_DIR/fo_007.txt" "FIELD OBSERVATIONS | FO-007"
            ;;
        "FO-008")
            mostrar_observacion "$DATA_DIR/fo_008.txt" "FIELD OBSERVATIONS | FO-008"
            ;;
        "FO-009")
            mostrar_observacion "$DATA_DIR/fo_009.txt" "FIELD OBSERVATIONS | FO-009"
            ;;
        "FO-010")
            mostrar_observacion "$DATA_DIR/fo_010.txt" "FIELD OBSERVATIONS | FO-010"
            ;;
        "FO-011")
            mostrar_observacion "$DATA_DIR/fo_011.txt" "FIELD OBSERVATIONS | FO-011"
            ;;
        "FO-012")
            mostrar_observacion "$DATA_DIR/fo_012.txt" "FIELD OBSERVATIONS | FO-012"
            ;;
        "FO-013")
            mostrar_observacion "$DATA_DIR/fo_013.txt" "FIELD OBSERVATIONS | FO-013"
            ;;
        "Volver"|"")
            break
            ;;
    esac
done
