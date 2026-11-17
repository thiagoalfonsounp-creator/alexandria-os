#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
CATEGORIA=ubicaciones
TITULO="ARCHIVO DE UBICACIONES"
INDEX="$PROJECT_ROOT/data/world/${CATEGORIA}_index.tsv"
command -v dialog >/dev/null || { echo 'Falta dialog.' >&2; exit 1; }
[[ -r "$INDEX" ]] || { dialog --msgbox "No se encontró el índice: $INDEX" 0 0; exit 1; }

mostrar_ficha() {
    local archivo="$1"
    local titulo="$2"
    local terminal_rows=24
    local terminal_cols=80
    local cuadro_alto
    local cuadro_ancho
    local ancho_texto
    local archivo_formateado
    local estado_dialog

    if [[ ! -r "$archivo" ]]; then
        dialog --title "$TITULO" \
            --msgbox "No se puede leer la ficha:\n$archivo" 0 0
        return 1
    fi

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
        dialog --title "$TITULO" \
            --msgbox "No se pudo preparar la ficha para mostrarla." 0 0
        return 1
    fi

    dialog --title "$titulo" --exit-label "Volver" \
        --textbox "$archivo_formateado" "$cuadro_alto" "$cuadro_ancho"
    estado_dialog=$?
    rm -f -- "$archivo_formateado"
    return "$estado_dialog"
}

declare -A rutas nombres
opciones=()
while IFS=$'\t' read -r id nombre tipo archivo; do
    [[ -z "$id" || "$id" == ID ]] && continue
    rutas["$id"]="$archivo"
    nombres["$id"]="$nombre"
    opciones+=("$id" "$nombre · $tipo")
done < "$INDEX"
(( ${#opciones[@]} )) || { dialog --msgbox 'El índice está vacío.' 0 0; exit 1; }
ultima="${opciones[0]}"
while true; do
    eleccion=$(dialog --title "$TITULO" --default-item "$ultima" \
        --cancel-label "Volver" --menu "Elegí una ficha · Contiene spoilers" \
        0 0 12 "${opciones[@]}" "volver" "Regresar a THE WORLD" 3>&1 1>&2 2>&3)
    estado=$?
    (( estado == 0 )) || break
    [[ "$eleccion" == volver ]] && break
    [[ -n "$eleccion" ]] || continue
    archivo="${rutas[$eleccion]:-}"
    if [[ -z "$archivo" || "$archivo" != data/world/* || "$archivo" == *..* || ! -r "$PROJECT_ROOT/$archivo" ]]; then
        dialog --msgbox 'No se puede abrir esta ficha.' 0 0
        continue
    fi
    ultima="$eleccion"
    mostrar_ficha "$PROJECT_ROOT/$archivo" "${nombres[$eleccion]}"
done
