#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
INDEX="$PROJECT_ROOT/data/world/recorrido_rick_index.tsv"

command -v dialog >/dev/null || { echo 'Falta dialog.' >&2; exit 1; }
[[ -r "$INDEX" ]] || { dialog --msgbox "No se encontró el índice: $INDEX" 0 0; exit 1; }

declare -A RUTAS TITULOS
OPCIONES=()
while IFS=$'\t' read -r id titulo referencia archivo; do
    [[ -z "$id" || "$id" == ID ]] && continue
    RUTAS["$id"]="$archivo"
    TITULOS["$id"]="$titulo"
    OPCIONES+=("$id" "$titulo" "$referencia")
done < "$INDEX"

if [[ ${#OPCIONES[@]} -eq 0 ]]; then
    dialog --msgbox 'El índice del recorrido está vacío.' 0 0
    exit 1
fi

ULTIMA="${OPCIONES[0]}"
while true; do
    ELECCION=$(dialog --title "THE WORLD | RECORRIDO DE RICK" \
        --default-item "$ULTIMA" --cancel-label "Volver" --item-help \
        --menu "Elegí un mapa o una etapa · Contiene spoilers" \
        0 0 12 "${OPCIONES[@]}" "VOLVER" "Regresar a THE WORLD" "" \
        3>&1 1>&2 2>&3)
    ESTADO=$?
    (( ESTADO == 0 )) || break
    [[ "$ELECCION" == VOLVER ]] && break

    ARCHIVO="${RUTAS[$ELECCION]:-}"
    if [[ -z "$ARCHIVO" || "$ARCHIVO" != data/world/recorrido_rick/* || \
          "$ARCHIVO" == *..* || ! -r "$PROJECT_ROOT/$ARCHIVO" ]]; then
        dialog --msgbox 'No se puede abrir esta entrada del recorrido.' 0 0
        continue
    fi

    ULTIMA="$ELECCION"
    dialog --title "${TITULOS[$ELECCION]}" --exit-label "Volver" \
        --textbox "$PROJECT_ROOT/$ARCHIVO" 0 0
done
