# Alexandria OS

Alexandria OS es un entorno de archivo y consulta basado en Debian 13 para el cómic principal de *The Walking Dead*, una biblioteca personal y módulos de supervivencia.

Repositorio privado y fuente de verdad: [thiagoalfonsounp-creator/alexandria-os](https://github.com/thiagoalfonsounp-creator/alexandria-os).

## Estado del proyecto — 7 de noviembre de 2026

- El código de la copia de trabajo y la documentación están sincronizados en la rama `main`.
- El archivo reúne 248 entradas: 225 personajes, 5 antagonistas principales, 14 caminantes identificados y 4 animales. Incluye 31 expedientes ampliados, 199 fichas breves y 18 identificaciones. Cada categoría tiene su selector y la lista se desplaza con el teclado.
- `THE WORLD` también conecta Comunidades (13 fichas), Ubicaciones (19), Glosario (40 términos y una guía de método) y Cronología (33 etapas y una guía de método). Sus menús vuelven a la categoría anterior con Escape.
- La propuesta de identidad visual está documentada en [`IDENTIDAD_VISUAL.md`](IDENTIDAD_VISUAL.md); es una guía de diseño, todavía no implementada en la interfaz.
- El selector agrega el arco y el número de primera aparición entre paréntesis cuando se confirmaron. Si falta esa verificación, muestra `Arco no confirmado`; el índice conserva `UNCONFIRMED`.
- Las fichas breves registran nombres y grupos de referencia sin inventar escenas, parentescos o destinos. Cuando falta comprobación directa del número del cómic, usan `UNCONFIRMED`.
- Se corrigieron nombres que provenían de la adaptación televisiva: el archivo usa Maggie Greene, Carol y Sophia Grimes en el epílogo. El cómic no establece para Carol el apellido Peletier.
- El usuario confirmó en Debian que la versión anterior de `WALKER DATABASE` y `FIELD OBSERVATIONS` funciona. La ampliación del archivo de personajes se incorporó al código, pero todavía no se ha probado en la VM.
- No se incluyen páginas, paneles ni archivos de cómics protegidos.

## Instalación y ejecución

La aplicación utiliza Bash, `dialog` y `nano`. El lector de PDF requiere `poppler-utils` (`pdfinfo` y `pdftoppm`) y `chafa`.

```bash
sudo apt update
sudo apt install bash dialog nano unzip poppler-utils chafa
```

Desde la raíz del proyecto:

```bash
./bin/alexandria
```

En los menús, usá las flechas y Enter. Escape cancela o vuelve al menú anterior. El selector de personajes se desplaza con las flechas y las teclas de página.

Algunos módulos del paquete todavía usan `/home/walker/alexandria-os` o `$HOME/alexandria-os`; mantené esa ruta o actualizá los scripts que la usan.

## Archivo de personajes

`data/world/personajes_index.tsv` conecta cada entrada con su ficha, categoría, agrupación, nivel de detalle y datos confirmados de primera aparición. `src/world/personajes.sh` carga el índice para personajes, antagonistas, caminantes y animales. Las fichas breves están en `data/world/personajes/`; los expedientes ampliados permanecen junto a los demás módulos de `data/world/`.

El alcance de este archivo principal es la serie regular, números 1-193, y el epílogo. El inventario usado para localizar nombres y sus exclusiones se documenta en `data/world/personajes_alcance.txt`. Se usa como índice terciario; los hechos narrativos se respaldan con números del cómic.

## Biblioteca personal

Guardá PDF o CBZ de tu propiedad en `imports/comics/`. No subas cómics protegidos al repositorio ni los incluyas en paquetes compartidos.

## Canon y evidencia

El archivo sigue el cómic principal y mantiene separados los hechos de escena, las observaciones de conducta y las declaraciones del autor. Las etiquetas de evidencia son `CONFIRMED`, `OBSERVED` y `UNCONFIRMED`. Los datos que el cómic no establece quedan abiertos.

## Estructura

```text
AGENTS.md               Reglas de canon, contenido y desarrollo
README.md               Estado, uso e historial
bin/                    Lanzador principal
src/world/              Menús y módulos de THE WORLD
src/comic_archive/      Catálogo y lector de cómics
config/                 Configuración
assets/                 Recursos de interfaz
data/world/             Expedientes y catálogos en texto
imports/comics/         Archivos personales locales; no se publican
docs/                   Documentación del proyecto
```

## Historial de trabajo

### 2026-11-07 — Documentación y sincronización del proyecto

- Se establecieron `AGENTS.md` y este README como reglas de trabajo y registro acumulativo.
- Se incorporó a GitHub el código fuente del paquete local junto con la documentación. El repositorio es privado y usa `main`.
- El usuario confirmó en Debian que `WALKER DATABASE` y `FIELD OBSERVATIONS` funcionaban.

### 2026-11-07 — Ampliación del archivo de personajes

- Se recuperó el inventario agrupado de personajes y se integraron 248 entradas en `personajes_index.tsv`, con fichas vinculadas a todas las rutas.
- Se separaron personajes, antagonistas principales, animales y caminantes identificados en los menús. Cada nombre muestra su arco y número de primera aparición cuando están confirmados; los datos pendientes conservan `UNCONFIRMED`.
- Se ampliaron expedientes de personajes principales y se añadieron fichas breves para secundarios. Las entradas sin verificación directa conservan `UNCONFIRMED` y no reciben números de edición inventados.
- Se ajustaron nombres y continuidad al cómic principal, y se documentaron los materiales complementarios que quedan fuera del selector.
- El código nuevo requiere comprobación en la VM Debian; la ejecución anterior no verifica esta ampliación.


### 2026-11-07 — Integración de la copia Debian con el índice de personajes

- La copia actual de Debian contiene 13 fichas de Comunidades, 19 de Ubicaciones, 41 entradas de Glosario y 34 etapas de Cronología. La rama `main` contiene el índice común de 248 fichas: 225 personajes, 5 antagonistas, 14 caminantes y 4 animales.
- La integración conecta Personajes, Antagonistas y Animales con el índice común.
- `personajes.sh` y el TSV del índice tenían finales de línea CRLF, que causaban el error `$'\r'`; ambos se normalizaron a LF. Después de la corrección, Thiago confirmó que la lista de Personajes abre.
- **Pendiente:** cotejar las fichas con números y escenas primarios. Las fichas no revisadas conservan `UNCONFIRMED`. La verificación confirmada se limita a la apertura de la lista de Personajes; no cubre las demás categorías.

### 2026-11-07 — Integración de Comunidades, Ubicaciones, Glosario y Cronología

- Se conectaron las cuatro categorías de la copia Debian al menú `THE WORLD`, con índices TSV y fichas de texto. Las categorías pueden abrirse desde el proyecto sin depender de la carpeta desde la que se inicia cada módulo.
- Se mantuvieron 13 comunidades, 19 ubicaciones, 40 términos de glosario y 33 etapas cronológicas; cada índice incluye también su guía de método cuando corresponde.
- Se fusionó el menú con el índice común de personajes de 248 entradas y se conservaron los selectores de Animales, Antagonistas y Caminantes. `personajes.sh` adapta el tamaño de sus ventanas al terminal.
- Se añadió `.gitattributes` para conservar finales de línea LF en Bash, TSV, TXT y Markdown, evitando que Windows reintroduzca el error `$'\r'`.
- Se incorporó [`IDENTIDAD_VISUAL.md`](IDENTIDAD_VISUAL.md) como propuesta pendiente; no se aplicaron cambios visuales a la interfaz.
- **Pendiente:** probar estas categorías integradas en la VM Debian y cotejar las referencias de las fichas con los ejemplares del cómic. No se registra como validada ninguna categoría que no se haya probado en la VM.


Al cerrar cada tarea, agregá una entrada cronológica a este historial sin borrar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.
