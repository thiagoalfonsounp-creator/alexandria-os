#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DATA_DIR="$PROJECT_ROOT/data/world"
INDEX_FILE="$DATA_DIR/personajes_index.tsv"
tipo_solicitado="${1:-PERSONAJE}"

case "$tipo_solicitado" in
    PERSONAJE) titulo="ARCHIVO DE PERSONAJES"; sustantivo="personajes" ;;
    ANTAGONISTA) titulo="BASE DE DATOS DE ANTAGONISTAS"; sustantivo="antagonistas" ;;
    CAMINANTE) titulo="CAMINANTES IDENTIFICADOS"; sustantivo="caminantes identificados" ;;
    ANIMAL) titulo="ARCHIVO DE ANIMALES"; sustantivo="animales" ;;
    *)
        dialog --title "THE WORLD" \
            --msgbox "Categoría no reconocida: $tipo_solicitado" 7 62
        exit 2
        ;;
esac

if [[ ! -r "$INDEX_FILE" ]]; then
    dialog --title "$titulo" \
        --msgbox "No se encontró el índice de personajes:\n$INDEX_FILE" 8 72
    exit 1
fi

declare -A archivo_por_etiqueta
opciones=()

while IFS=$'\t' read -r personaje grupo tipo nivel arco primera_aparicion archivo; do
    [[ "$personaje" == "PERSONAJE" || -z "$personaje" || -z "$archivo" ]] && continue
    [[ "$tipo" == "$tipo_solicitado" ]] || continue

    case "$nivel" in
        AMPLIADO) estado="Expediente ampliado" ;;
        BREVE) estado="Ficha breve" ;;
        IDENTIFICACIÓN)
            case "$tipo" in
                CAMINANTE) estado="Caminante identificado" ;;
                ANIMAL) estado="Animal identificado" ;;
            esac
            ;;
        *) estado="Ficha" ;;
    esac

    if [[ -n "$arco" && "$arco" != "UNCONFIRMED" ]]; then
        if [[ -n "$primera_aparicion" && "$primera_aparicion" != "UNCONFIRMED" ]]; then
            etiqueta="$personaje ($arco · $primera_aparicion)"
        else
            etiqueta="$personaje ($arco)"
        fi
    else
        etiqueta="$personaje (Arco no confirmado)"
    fi

    opciones+=("$etiqueta" "$estado · $grupo")
    archivo_por_etiqueta["$etiqueta"]="$archivo"
done < "$INDEX_FILE"

if (( ${#opciones[@]} == 0 )); then
    dialog --title "$titulo" \
        --msgbox "No hay fichas en la categoría $sustantivo." 7 64
    exit 0
fi


ANCHO_VENTANA=96
ANCHO_RETRATO=20
SEPARACION=2
columnas_terminal=$(tput cols 2>/dev/null || true)
lineas_terminal=$(tput lines 2>/dev/null || true)
if [[ "$columnas_terminal" =~ ^[0-9]+$ ]] && (( columnas_terminal > 0 && columnas_terminal < ANCHO_VENTANA )); then
    ANCHO_VENTANA=$((columnas_terminal - 2))
fi
if (( ANCHO_VENTANA < 76 )); then
    ANCHO_RETRATO=18
    SEPARACION=2
fi
if (( ANCHO_VENTANA < 60 )); then
    ANCHO_RETRATO=14
    SEPARACION=1
fi
ANCHO_TEXTO=$((ANCHO_VENTANA - ANCHO_RETRATO - SEPARACION - 6))
if (( ANCHO_TEXTO < 24 )); then
    ANCHO_TEXTO=24
    ANCHO_VENTANA=$((ANCHO_TEXTO + ANCHO_RETRATO + SEPARACION + 6))
fi

ALTURA_VENTANA=36
if [[ "$lineas_terminal" =~ ^[0-9]+$ ]] && (( lineas_terminal > 0 )); then
    ALTURA_VENTANA=$((lineas_terminal - 2))
fi
if (( ALTURA_VENTANA < 12 )); then
    ALTURA_VENTANA=12
fi

crear_vista_ficha() {
    local archivo_ficha="$1"
    local archivo_salida="$2"
    local nombre_base="${archivo_ficha##*/}"
    local extension imagen="" borde espacio fila max_filas indice
    local -a lineas_texto=()
    local -a filas_retrato=()
    local -a salida_chafa=()

    nombre_base="${nombre_base%.txt}"
    mapfile -t lineas_texto < <(
        sed 's/\r$//' "$archivo_ficha" |
        awk '
            function emitir_parrafo() {
                if (parrafo != "") {
                    print parrafo
                    parrafo = ""
                }
            }
            {
                linea = $0
                if (linea ~ /^[[:space:]]*$/) {
                    emitir_parrafo()
                    print ""
                    next
                }
                if (linea == toupper(linea) || linea ~ /^[[:alpha:]][[:alpha:][:space:]_.-]*:/) {
                    emitir_parrafo()
                    print linea
                    next
                }
                if (parrafo == "") parrafo = linea
                else parrafo = parrafo " " linea
            }
            END { emitir_parrafo() }
        ' |
        fold -s -w "$ANCHO_TEXTO"
    )

    borde="+$(printf '%*s' "$((ANCHO_RETRATO - 2))" '' | tr ' ' '-')+"
    espacio="|$(printf '%*s' "$((ANCHO_RETRATO - 2))" '')|"

    for extension in png jpg jpeg webp gif; do
        if [[ -r "$DATA_DIR/retratos/$nombre_base.$extension" ]]; then
            imagen="$DATA_DIR/retratos/$nombre_base.$extension"
            break
        fi
    done

    if [[ -n "$imagen" ]] && command -v chafa >/dev/null 2>&1; then
        mapfile -t salida_chafa < <(chafa --format symbols --colors none --symbols braille --invert --relative off --size "$((ANCHO_RETRATO - 2))x20" "$imagen" 2>/dev/null)
        if ((${#salida_chafa[@]} > 0)); then
            filas_retrato+=("$borde")
            for fila in "${salida_chafa[@]}"; do
                filas_retrato+=("$(printf '|%-*s|' "$((ANCHO_RETRATO - 2))" "$fila")")
            done
            filas_retrato+=("$borde")
        fi
    fi

    if ((${#filas_retrato[@]} == 0)); then
        filas_retrato=(
            "$borde"
            "$espacio"
            "$(printf '| %-*s |' "$((ANCHO_RETRATO - 4))" "RETRATO")"
            "$(printf '| %-*s |' "$((ANCHO_RETRATO - 4))" "PENDIENTE")"
            "$espacio"
            "$borde"
        )
    fi

    max_filas=${#lineas_texto[@]}
    if ((${#filas_retrato[@]} > max_filas)); then
        max_filas=${#filas_retrato[@]}
    fi

    : > "$archivo_salida"
    for ((indice = 0; indice < max_filas; indice++)); do
        printf "%-*s%*s%-*s\n" "$ANCHO_TEXTO" "${lineas_texto[indice]:-}" "$SEPARACION" "" "$ANCHO_RETRATO" "${filas_retrato[indice]:-}" >> "$archivo_salida"
    done
}


while true; do
    etiqueta=$(dialog --title "$titulo" \
        --menu "Elegí qué expediente querés consultar" 0 0 14 \
        "${opciones[@]}" \
        "__VOLVER__" "Regresar a THE WORLD" \
        3>&1 1>&2 2>&3)
    estado_dialog=$?

    if (( estado_dialog != 0 )) || [[ "$etiqueta" == "__VOLVER__" ]]; then
        break
    fi

    archivo="${archivo_por_etiqueta[$etiqueta]:-}"
    if [[ -z "$archivo" || ! -r "$PROJECT_ROOT/$archivo" ]]; then
        dialog --title "$titulo" \
            --msgbox "No se puede abrir la ficha seleccionada." 7 58
        continue
    fi

    vista_temporal=$(mktemp "${TMPDIR:-/tmp}/alexandria-ficha.XXXXXX")
    if [[ -z "$vista_temporal" ]]; then
        dialog --title "$titulo" --msgbox "No se pudo preparar la vista de la ficha." 7 62
        continue
    fi
    crear_vista_ficha "$PROJECT_ROOT/$archivo" "$vista_temporal"
    dialog --title "$titulo | $etiqueta" --textbox "$vista_temporal" "$ALTURA_VENTANA" "$ANCHO_VENTANA"
    rm -f -- "$vista_temporal"
done
