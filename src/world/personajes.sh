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

while true; do
    etiqueta=$(dialog --title "$titulo" \
        --menu "Elegí qué expediente querés consultar" 28 110 14 \
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

    dialog --title "$titulo | $etiqueta" \
        --textbox "$PROJECT_ROOT/$archivo" 28 110
done
