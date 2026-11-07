#!/bin/bash

while true; do
    antagonista=$(dialog --title "BASE DE DATOS DE ANTAGONISTAS" \
        --menu "Elegí qué expediente querés consultar" 18 72 6 \
        "Shane Walsh" "Antagonista; expediente disponible" \
        "El Gobernador" "Antagonista; expediente disponible" \
        "Negan" "Antagonista; expediente disponible" \
        "Alpha" "Antagonista; expediente disponible" \
        "Beta" "Antagonista; expediente disponible" \
        "Volver" "Regresar a THE WORLD" \
        3>&1 1>&2 2>&3)

    case "$antagonista" in
        "Shane Walsh")
            dialog --title "EXPEDIENTE: SHANE WALSH" \
                --textbox "$HOME/alexandria-os/data/world/shane_walsh.txt" 28 110
            ;;
        "El Gobernador")
            dialog --title "EXPEDIENTE: EL GOBERNADOR" \
                --textbox "$HOME/alexandria-os/data/world/el_gobernador.txt" 28 110
            ;;
        "Negan")
            dialog --title "EXPEDIENTE: NEGAN" \
                --textbox "$HOME/alexandria-os/data/world/negan.txt" 28 110
            ;;
        "Alpha")
            dialog --title "EXPEDIENTE: ALPHA" \
                --textbox "$HOME/alexandria-os/data/world/alpha.txt" 28 110
            ;;
        "Beta")
            dialog --title "EXPEDIENTE: BETA" \
                --textbox "$HOME/alexandria-os/data/world/beta.txt" 28 110
            ;;
        "Volver"|"")
            break
            ;;
    esac
done
