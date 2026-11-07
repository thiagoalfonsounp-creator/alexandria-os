#!/bin/bash

while true; do
    categoria=$(dialog --title "THE WORLD" \
        --menu "Elegí una categoría" 20 72 10 \
        "Personajes" "Protagonistas y secundarios" \
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
            bash "$HOME/alexandria-os/src/world/personajes.sh"
            ;;
        "Caminantes")
            bash "$HOME/alexandria-os/src/world/caminantes.sh"
            ;;
        "Antagonistas")
            bash "$HOME/alexandria-os/src/world/antagonistas.sh"
            ;;
        "Observaciones")
            bash "$HOME/alexandria-os/src/world/observaciones.sh"
            ;;
        "Volver"|"")
            break
            ;;
        *)
            dialog --title "THE WORLD" \
                --msgbox "La sección '$categoria' está planificada y se incorporará más adelante." 8 64
            ;;
    esac
done
