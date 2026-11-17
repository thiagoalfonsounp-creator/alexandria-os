#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
ROOT="$PROJECT_ROOT"
DATA_DIR="$ROOT/data/world/walker_database"

mostrar_archivo() {
    local archivo="$1"
    local titulo="$2"

    if [[ ! -r "$archivo" ]]; then
        dialog --title "WALKER DATABASE" \
            --msgbox "No se puede leer el archivo del expediente:\n$archivo" 0 0
    elif [[ ! -s "$archivo" ]]; then
        dialog --title "WALKER DATABASE" \
            --msgbox "El archivo del expediente está vacío:\n$archivo" 0 0
    else
        dialog --title "$titulo" --textbox "$archivo" 0 0
    fi
}

while true; do
    seccion=$(dialog --title "WALKER DATABASE" \
        --menu "Elegí un apartado del archivo" 0 0 10 \
        "Caminantes identificados" "Individuos del cómic identificados" \
        "Perfil" "Alcance, identidad y criterio de evidencia" \
        "Anatomía y daño" "Cabeza, cerebro y lesiones" \
        "Infección y reanimación" "Mordidas, muerte y retorno" \
        "Movilidad y sentidos" "Olor, ruido y deterioro" \
        "Conducta y clasificaciones" "Roamer, lurker y hordas" \
        "Debilidades y casos especiales" "Límites documentados" \
        "Referencias y pendientes" "Fuentes y dudas abiertas" \
        "Volver" "Regresar a THE WORLD" \
        3>&1 1>&2 2>&3)

    case "$seccion" in
        "Caminantes identificados")
            bash "$SCRIPT_DIR/personajes.sh" CAMINANTE
            ;;
        "Perfil")
            mostrar_archivo "$DATA_DIR/perfil.txt" "WALKER DATABASE | PERFIL"
            ;;
        "Anatomía y daño")
            mostrar_archivo "$DATA_DIR/anatomia_dano.txt" "WALKER DATABASE | ANATOMÍA Y DAÑO"
            ;;
        "Infección y reanimación")
            mostrar_archivo "$DATA_DIR/infeccion_reanimacion.txt" "WALKER DATABASE | INFECCIÓN Y REANIMACIÓN"
            ;;
        "Movilidad y sentidos")
            mostrar_archivo "$DATA_DIR/movilidad_sentidos.txt" "WALKER DATABASE | MOVILIDAD Y SENTIDOS"
            ;;
        "Conducta y clasificaciones")
            mostrar_archivo "$DATA_DIR/conducta_clasificaciones.txt" "WALKER DATABASE | CONDUCTA Y CLASIFICACIONES"
            ;;
        "Debilidades y casos especiales")
            mostrar_archivo "$DATA_DIR/debilidades_casos.txt" "WALKER DATABASE | DEBILIDADES Y CASOS ESPECIALES"
            ;;
        "Referencias y pendientes")
            mostrar_archivo "$DATA_DIR/referencias_evidencia.txt" "WALKER DATABASE | REFERENCIAS"
            ;;
        "Volver"|"")
            break
            ;;
    esac
done
