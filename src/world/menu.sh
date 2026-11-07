#!/usr/bin/env bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

while true; do
    categoria=$(dialog --title "THE WORLD" \
        --menu "Elegí una categoría" 20 72 10 \
        "Personajes" "Protagonistas y secundarios" \
        "Animales" "Animales identificados del cómic" \
        "Caminantes" "WALKER DATABASE" \
        "Antagonistas" "Amenazas y conflictos" \
        "Comunidades" "Grupos y organización" \
        "Ubicaciones" "Lugares relevantes" \
        "Cronología" "Orden de acontecimientos" \
        "Observaciones" "FIELD OBSERVATIONS" \
        "Glosario" "Términos del universo" \
        "Recorrido de Rick" "Mapas y etapas del viaje" \
        "Volver" "Menú principal" \
        3>&1 1>&2 2>&3)

    case "$categoria" in
        "Personajes")
            bash "$SCRIPT_DIR/personajes.sh" PERSONAJE
            ;;
        "Animales")
            bash "$SCRIPT_DIR/personajes.sh" ANIMAL
            ;;
        "Caminantes")
            bash "$SCRIPT_DIR/caminantes.sh"
            ;;
        "Antagonistas")
            bash "$SCRIPT_DIR/personajes.sh" ANTAGONISTA
            ;;
        "Comunidades")
            bash "$SCRIPT_DIR/comunidades.sh"
            ;;
        "Ubicaciones")
            bash "$SCRIPT_DIR/ubicaciones.sh"
            ;;
        "Observaciones")
            bash "$SCRIPT_DIR/observaciones.sh"
            ;;
        "Volver"|"")
            break
            ;;
        "Glosario")
            bash "$SCRIPT_DIR/glosario.sh"
            ;;
        "Cronología")
            bash "$SCRIPT_DIR/cronologia.sh"
            ;;
        *)
            dialog --title "THE WORLD" \
                --msgbox "La sección '$categoria' está planificada y se incorporará más adelante." 8 64
            ;;
    esac
done
