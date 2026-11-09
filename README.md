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
sudo apt install bash dialog nano unzip poppler-utils chafa python3
```

Desde la raíz del proyecto:

```bash
./bin/alexandria
```

En los menús, usá las flechas y Enter. Escape cancela o vuelve al menú anterior. El selector de personajes se desplaza con las flechas y las teclas de página.

Algunos módulos del paquete todavía usan `/home/walker/alexandria-os` o `$HOME/alexandria-os`; mantené esa ruta o actualizá los scripts que la usan.

## THE REFUGE

El menú principal abre `src/refuge/refuge.py` desde la opción **THE REFUGE**. La primera versión jugable es una campaña breve de terminal con consejo, expedición, crisis, tres turnos de guerra y una decisión final. Las elecciones alteran suministros, supervivientes, moral, defensas, inteligencia, alianzas y el desenlace.

La campaña se guarda localmente como JSON en `$XDG_STATE_HOME/alexandria-os/the-refuge.json`; si `XDG_STATE_HOME` no está definido, usa `~/.local/state/alexandria-os/the-refuge.json`. Los datos guardados no se escriben en el repositorio.

La historia presenta una variación original inspirada en el arco *All-Out War*. Image Comics identifica el número [#115](https://imagecomics.com/comics/releases/the-walking-dead-115) como su inicio y el [#126](https://imagecomics.com/comics/releases/the-walking-dead-126) como su conclusión. Los valores, decisiones y finales de la campaña son mecánicas de juego y no alteran el canon.

**Validación:** el código está conectado al lanzador en `main`; todavía no se ejecutó en la VM Debian. La próxima comprobación debe hacerse desde el menú de Alexandria y confirmar guardado, reanudación y un desenlace.

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

### 2026-11-09 14:27 ART — Presentación vertical de fichas

- `src/world/personajes.sh` prepara una vista temporal con líneas envueltas en una columna izquierda y una ventana de ancho uniforme; el ancho se adapta a terminales más angostas.
- Se reserva a la derecha un panel de 28 columnas. Si existe una imagen con el mismo nombre base del expediente en `data/world/retratos/` (PNG, JPG, JPEG, WebP o GIF), `chafa` la convierte a caracteres Unicode monocromos; sin imagen aparece `RETRATO PENDIENTE`.
- No se añadieron imágenes. Los retratos para el repositorio deben ser originales o contar con autorización; no se incorporan páginas ni paneles del cómic.
- **Validación:** el cambio de código quedó en la rama `main`; no se ejecutó en la VM Debian.
- **Pendiente:** copiar la actualización a Debian y comprobar visualmente Personajes, Antagonistas, Animales y Caminantes, además de probar un retrato local.

### 2026-11-09 15:12 ART — Ajuste del panel de retratos

- La captura de Debian mostró que el retrato ya cargaba, pero la conversión monocroma quedaba demasiado oscura y casi cuadrada.
- Se añadió `--invert` para el fondo claro de `dialog` y se amplió la salida de 14 a 18 filas, conservando el panel compacto.
- **Validación:** la captura confirma carga y encuadre de la imagen con la versión anterior; el nuevo ajuste aún no se comprobó en Debian.
- **Pendiente:** copiar el script actualizado a la VM y revisar una ficha con retrato.

### 2026-11-09 3:17:35 PM ART — Ajuste de proporciones de fichas

- La captura de Debian mostró demasiado ancho vacío a la derecha y un panel de retrato sobredimensionado.
- Se redujo la ventana máxima a 88 columnas, el panel a 22 columnas y el render a 16 filas; el texto sigue ajustándose al ancho de la terminal.
- **Validación:** el usuario confirmó el resultado de la versión anterior; estas nuevas proporciones todavía no se comprobaron en Debian.
- **Pendiente:** copiar el script actualizado a la VM y revisar una ficha con retrato.


### 2026-11-09 — Reflujo del texto y equilibrio del retrato

- Se fijó el ancho de la ficha en 96 columnas y se ajustó la altura al terminal. En terminales más angostas, el panel del retrato se reduce.
- El panel del retrato quedó en 20 columnas, separado por 2; los renglones consecutivos del texto ahora se recomponen como párrafos antes de envolverse, para evitar fragmentos cortos.
- **Validación:** el cambio quedó en `main`; todavía no se ha comprobado en la VM Debian.
- **Pendiente:** copiar el script actualizado a Debian y revisar una ficha con retrato.



### 2026-11-09 — Más detalle en retratos monocromos

- Se cambió el render de Chafa a símbolos Braille, que permiten representar más detalle dentro de las mismas celdas. El panel conserva su ancho de 20 columnas y el límite de salida del retrato pasa a 20 filas.
- El retrato sigue siendo una aproximación de caracteres dentro del visor de texto, no una imagen rasterizada.
- **Validación:** cambio publicado en `main`; falta comprobar cómo se representa en la VM Debian.
- **Pendiente:** copiar el script actualizado y revisar el retrato en pantalla.



### 2026-11-09 — Ajuste de detalle del retrato textual

- La captura mostró que el modo Braille quedaba demasiado punteado. Se reemplazó por símbolos de mosaico Sextant y se amplió el panel a 28 columnas en terminales anchas; la geometría se reduce en terminales más angostas.
- El retrato se mantiene dentro de la interfaz textual de `dialog`; no se introdujeron interfaces gráficas ni se presenta como imagen rasterizada.
- **Validación:** código actualizado en `main`; este modo todavía no se comprobó en Debian.
- **Pendiente:** transferir el script a la VM y revisar una ficha con retrato.



### 2026-11-09 — Validación visual del retrato de Rick

- La captura de Debian muestra la ficha de Rick Grimes con el retrato representado mediante mosaicos Sextant en el panel derecho y el texto legible en la columna izquierda.
- El usuario confirmó que esta presentación le convence.
- **Alcance:** se valida visualmente esta ficha de Rick. No se registran como verificadas todas las fichas, Antagonistas ni Animales.



### 2026-11-09 — Retratos selectivos por relevancia

- El visor reserva panel para expedientes `AMPLIADO` y para las fichas breves enumeradas en `data/world/retratos_destacados.txt`.
- Las demás fichas se muestran sin panel de retrato, en un cuadro de texto más compacto. La lista curada inicial incluye a Allen, Axel, Dexter, Duane, Judith, Rachel y Reggie.
- El RAR adjunto contiene 38 imágenes: los nombres coinciden con los 31 expedientes ampliados y los 7 secundarios seleccionados. Los binarios aún deben copiarse a `data/world/retratos/` en Debian.
- **Validación:** el cambio de código quedó en `main`; la captura anterior confirma el retrato de Rick, pero el filtro nuevo aún no se ha comprobado en la VM.
- **Pendiente:** transferir el script, la lista y las imágenes a Debian; revisar una ficha breve sin retrato y otra incluida en la lista.



### 2026-11-09 — Retratos selectivos copiados y verificados

- Se copiaron a la VM Debian el visor actualizado, la lista `data/world/retratos_destacados.txt` y los retratos en `data/world/retratos/`.
- En Debian se confirmaron los conteos esperados: 7 nombres en la lista curada y 38 archivos de imagen. El conjunto corresponde a los 31 expedientes ampliados y 7 fichas breves seleccionadas.
- El usuario confirmó el resultado esperado al consultar una ficha ampliada y una ficha breve incluida en la selección.
- **Alcance:** la comprobación visual se limita a las fichas consultadas; no valida todos los expedientes ni todas las categorías. Queda pendiente revisar una ficha breve fuera de la selección y comprobar las categorías restantes en Debian.


### 2026-11-09 — Primera versión jugable de THE REFUGE

- Se creó `src/refuge/refuge.py` y se conectó la opción **THE REFUGE** de `bin/alexandria` al módulo de terminal.
- La campaña persistente contiene consejo, expedición, crisis, tres turnos de guerra contra los Salvadores y una decisión final frente a Negan. Las decisiones cambian suministros, supervivientes, moral, defensas, inteligencia, alianzas y el desenlace.
- El estado se guarda localmente en JSON para permitir continuar la partida; no se guarda dentro del repositorio. La narrativa y los desenlaces son variaciones originales, sin reproducir páginas ni diálogos del cómic.
- Se añadió `python3` a las dependencias de instalación. Las referencias temáticas se limitaron a la ficha oficial de Image Comics para los números [#115](https://imagecomics.com/comics/releases/the-walking-dead-115) y [#126](https://imagecomics.com/comics/releases/the-walking-dead-126).
- **Validación:** código y conexión al menú confirmados en GitHub `main`; no ejecutado en Debian.
- **Pendiente:** instalar/copiar la actualización en la VM y comprobar navegación, persistencia JSON, reanudación y desenlaces.

Al cerrar cada tarea, agregá una entrada cronológica a este historial sin borrar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.
