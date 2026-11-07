#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
INDEX="$PROJECT_ROOT/data/world/glosario_index.tsv"
command -v dialog >/dev/null || { echo 'Falta dialog.' >&2; exit 1; }
[[ -r "$INDEX" ]] || { dialog --msgbox "No se encontró el índice: $INDEX" 0 0; exit 1; }
declare -A RUTAS NOMBRES
OPCIONES=()
while IFS=$'\t' read -r id nombre referencia archivo; do
    [[ -z "$id" || "$id" == ID ]] && continue
    RUTAS["$id"]="$archivo"
    NOMBRES["$id"]="$nombre"
    OPCIONES+=("$id" "$nombre" "$referencia")
done < "$INDEX"
if [[ ${#OPCIONES[@]} -eq 0 ]]; then
    dialog --msgbox 'El índice está vacío.' 0 0
    exit 1
fi
ULTIMA="${OPCIONES[0]}"
while true; do
    ELECCION=$(dialog --title "GLOSARIO DEL CÓMIC" --default-item "$ULTIMA" \
        --cancel-label "Volver" --item-help --menu "Elegí un término; la referencia sirve como localizador." \
        0 0 12 "${OPCIONES[@]}" "VOLVER" "Regresar a THE WORLD" "" 3>&1 1>&2 2>&3)
    ESTADO=$?
    (( ESTADO == 0 )) || break
    [[ "$ELECCION" == VOLVER ]] && break
    ARCHIVO="${RUTAS[$ELECCION]:-}"
    if [[ -z "$ARCHIVO" || "$ARCHIVO" != data/world/* || "$ARCHIVO" == *..* || ! -r "$PROJECT_ROOT/$ARCHIVO" ]]; then
        dialog --msgbox 'No se puede abrir esta entrada.' 0 0
        continue
    fi
    ULTIMA="$ELECCION"
    dialog --title "${NOMBRES[$ELECCION]}" --exit-label "Volver" \
        --textbox "$PROJECT_ROOT/$ARCHIVO" 0 0
done
