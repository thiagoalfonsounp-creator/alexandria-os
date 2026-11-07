#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
CATEGORIA=ubicaciones
TITULO="ARCHIVO DE UBICACIONES"
INDEX="$PROJECT_ROOT/data/world/${CATEGORIA}_index.tsv"
command -v dialog >/dev/null || { echo 'Falta dialog.' >&2; exit 1; }
[[ -r "$INDEX" ]] || { dialog --msgbox "No se encontró el índice: $INDEX" 0 0; exit 1; }
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
    dialog --title "${nombres[$eleccion]}" --exit-label "Volver" \
        --textbox "$PROJECT_ROOT/$archivo" 0 0
done
