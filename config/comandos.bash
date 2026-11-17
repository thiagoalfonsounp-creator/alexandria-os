# Comandos personalizados de Alexandria OS.
# Este archivo se carga desde ~/.bashrc mediante bin/instalar-comandos.

ALEXANDRIA_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export ALEXANDRIA_ROOT
export DIALOGRC="$ALEXANDRIA_ROOT/config/dialogrc"
if ! dialog --print-maxsize >/dev/null 2>&1; then
    unset DIALOGRC
fi

_alexandria_abrir_script() {
    local relativo="$1"
    shift
    local script="$ALEXANDRIA_ROOT/$relativo"

    if [[ ! -f "$script" ]]; then
        printf 'No encuentro el módulo de Alexandria OS en %s.\n' "$script" >&2
        return 1
    fi

    bash "$script" "$@"
}

alexandria() {
    _alexandria_abrir_script bin/alexandria "$@"
}

theworld() {
    _alexandria_abrir_script src/world/menu.sh "$@"
}

mundo() {
    theworld "$@"
}

personajes() {
    _alexandria_abrir_script src/world/personajes.sh PERSONAJE "$@"
}

antagonistas() {
    _alexandria_abrir_script src/world/personajes.sh ANTAGONISTA "$@"
}

animales() {
    _alexandria_abrir_script src/world/personajes.sh ANIMAL "$@"
}

caminantes() {
    _alexandria_abrir_script src/world/caminantes.sh "$@"
}

comicarchive() {
    _alexandria_abrir_script src/comic_archive/menu.sh "$@"
}

leertomo() {
    local lector="$ALEXANDRIA_ROOT/src/comic_archive/lector_pdf.sh"
    local dependencia

    if [[ ! -f "$lector" ]]; then
        printf 'No encuentro el lector de PDF en %s.\n' "$lector" >&2
        return 1
    fi

    for dependencia in dialog pdfinfo pdftoppm; do
        if ! command -v "$dependencia" >/dev/null 2>&1; then
            printf 'Falta el comando %s. Instalá las dependencias indicadas en el README de Alexandria OS.\n' "$dependencia" >&2
            return 127
        fi
    done

    if ! command -v chafa >/dev/null 2>&1 && \
        { ! command -v fbi >/dev/null 2>&1 || ! command -v fbgs >/dev/null 2>&1 || ! command -v gs >/dev/null 2>&1; }; then
        printf 'Falta un visor de páginas: instalá chafa para SSH o fbi y ghostscript para la consola local.\n' >&2
        return 127
    fi

    bash "$lector" "$@"
}

recorridorick() {
    _alexandria_abrir_script src/world/recorrido_rick.sh "$@"
}

comunidades() {
    _alexandria_abrir_script src/world/comunidades.sh "$@"
}

ubicaciones() {
    _alexandria_abrir_script src/world/ubicaciones.sh "$@"
}

glosario() {
    _alexandria_abrir_script src/world/glosario.sh "$@"
}

cronologia() {
    _alexandria_abrir_script src/world/cronologia.sh "$@"
}

observaciones() {
    _alexandria_abrir_script src/world/observaciones.sh "$@"
}

refugio() {
    if ! command -v python3 >/dev/null 2>&1; then
        printf 'Falta python3, necesario para THE REFUGE.\n' >&2
        return 127
    fi
    python3 "$ALEXANDRIA_ROOT/src/refuge/refuge.py" "$@"
}

refugiominijuegos() {
    refugio --probar-minijuegos "$@"
}

pruebaruta() {
    refugio --probar-minijuego ruta "$@"
}

pruebabrecha() {
    refugio --probar-minijuego brecha "$@"
}

pruebaradio() {
    refugio --probar-minijuego radio "$@"
}

pruebafinal() {
    refugio --probar-minijuego arena "$@"
}

pruebahorda() {
    refugio --probar-minijuego horda "$@"
}

cuaderno() {
    if ! command -v nano >/dev/null 2>&1; then
        printf 'Falta nano, necesario para abrir el cuaderno.\n' >&2
        return 127
    fi
    nano "$ALEXANDRIA_ROOT/data/cuaderno.txt" "$@"
}

fichapersonaje() {
    if [[ $# -eq 0 ]]; then
        printf 'Uso: fichapersonaje "Nombre exacto", por ejemplo: fichapersonaje "Rick Grimes"\n' >&2
        return 2
    fi
    _alexandria_abrir_script src/world/personajes.sh PERSONAJE "$*"
}

fichaantagonista() {
    if [[ $# -eq 0 ]]; then
        printf 'Uso: fichaantagonista "Nombre exacto", por ejemplo: fichaantagonista "Negan"\n' >&2
        return 2
    fi
    _alexandria_abrir_script src/world/personajes.sh ANTAGONISTA "$*"
}

rick() { fichapersonaje "Rick Grimes"; }
carl() { fichapersonaje "Carl Grimes"; }
lorigrimes() { fichapersonaje "Lori Grimes"; }
lori() { lorigrimes; }
michonne() { fichapersonaje "Michonne"; }
glenn() { fichapersonaje "Glenn Rhee"; }
maggie() { fichapersonaje "Maggie Greene"; }
andrea() { fichapersonaje "Andrea"; }
carol() { fichapersonaje "Carol"; }
dale() { fichapersonaje "Dale"; }
ezequiel() { fichapersonaje "Ezekiel"; }
eugene() { fichapersonaje "Eugene Porter"; }
abraham() { fichapersonaje "Abraham Ford"; }
negan() { fichaantagonista "Negan"; }
shane() { fichaantagonista "Shane Walsh"; }
alpha() { fichaantagonista "Alpha"; }
beta() { fichaantagonista "Beta"; }
gobernador() { fichaantagonista "Brian Blake (el Gobernador)"; }

comandosalexandria() {
    cat <<'AYUDA'
COMANDOS DE ALEXANDRIA OS

Inicio y archivo:
  alexandria       Menú principal
  comicarchive     Biblioteca de cómics
  leertomo         Elegir y leer un PDF
  cuaderno         Abrir el cuaderno de campo
  refugio          Abrir THE REFUGE
  refugiominijuegos Banco de pruebas sin cargar la campaña
  pruebaruta       Probar la ruta (inicial, media o avanzada)
  pruebabrecha     Probar las cuatro señales del perímetro
  pruebaradio      Probar la clave (inicial, media o avanzada)
  pruebahorda      Probar el evento QTE de la horda
  pruebafinal      Probar la arena de 40 segundos

THE WORLD:
  mundo            Menú de THE WORLD
  personajes       Selector de personajes
  antagonistas     Selector de antagonistas
  animales         Archivo de animales
  caminantes       WALKER DATABASE
  comunidades      Archivo de comunidades
  ubicaciones      Archivo de ubicaciones
  cronologia       Cronología del cómic
  glosario         Glosario del cómic
  observaciones    FIELD OBSERVATIONS
  recorridorick    Mapas y etapas del recorrido de Rick

Fichas directas:
  fichapersonaje "Nombre exacto"
  fichaantagonista "Nombre exacto"
  rick, carl, lori, lorigrimes, michonne, glenn, maggie, carol, dale,
  andrea, ezequiel, eugene, abraham, negan, shane, alpha, beta,
  gobernador
AYUDA
}
