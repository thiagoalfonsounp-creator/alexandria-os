# Alexandria OS

Alexandria OS 0.6 (desarrollo) es un entorno de archivo y consulta basado en Debian 13 para el cómic principal de *The Walking Dead*, una biblioteca personal y módulos de supervivencia.

Repositorio privado y fuente de verdad: [thiagoalfonsounp-creator/alexandria-os](https://github.com/thiagoalfonsounp-creator/alexandria-os).

## Continuación 0.6 — logo aprobado (2026-11-16 22:14 ART)

El menú principal usa el logo aprobado en [`assets/logo-alexandria-safe-zone.png`](assets/logo-alexandria-safe-zone.png). `src/ui/main_menu.py` lo representa con Chafa en caracteres a color, a la izquierda del menú. Esta distribución conserva la proporción del PNG y deja las opciones legibles en terminales de 80×24 y 120×40.

`python3 tests/smoke_terminal.py` pasó en ambos tamaños dentro de un pseudoterminal: comprobó la presencia de la imagen, la posición del menú, la apertura de ayuda, THE WORLD y THE REFUGE, y la salida a consola. El propietario confirmó que las pruebas manuales de 0.4 ya estaban aprobadas; ese antecedente se registra como confirmación suya, sin evidencias individuales adjuntas. Las regresiones y novedades de 0.6 siguen pendientes en la VM de entrega. La prueba automatizada de humo no sustituye esa revisión manual. Ver la [matriz de regresión 0.6](docs/MATRIZ_PRUEBAS_MANUALES_0.6.md) y la [matriz histórica 0.4](docs/MATRIZ_PRUEBAS_MANUALES_0.4.md).

La OVA y el PDF final permanecen fuera de Git y pendientes de validación. Detalles y límites: [Continuación 0.6](docs/CONTINUACION_0.6.md).

## Estado del proyecto — 11 de noviembre de 2026

- La captura del propietario del 10 de noviembre confirma Alexandria OS **0.5** en Debian con el menú principal abierto y el nuevo tema visual aplicado: fondo negro, panel claro y selección roja.
- El lanzador y el manual de esta copia muestran **Alexandria OS 0.6**.
- El índice reúne 249 asignaciones de categoría y 248 perfiles únicos: 225 personajes, 6 antagonistas (incluida Pamela Milton como antagonista secundaria), 14 caminantes identificados y 4 animales. Pamela aparece en Personajes y Antagonistas y comparte ficha. Cada categoría tiene su selector y la lista se desplaza con el teclado.
- `THE WORLD` también conecta Comunidades (13 fichas), Ubicaciones (19), Glosario (40 términos y una guía de método) y Cronología (33 etapas y una guía de método). Sus menús vuelven a la categoría anterior con Escape.
- La entrega académica final sigue pendiente: imagen virtual Debian `.ova` e informe exclusivamente en PDF, según los requisitos registrados en `AGENTS.md`.
- `Recorrido de Rick` está conectado al menú de `THE WORLD` mediante `src/world/menu.sh` y `src/world/recorrido_rick.sh`. Su índice `data/world/recorrido_rick_index.tsv` reúne 14 entradas: tres mapas esquemáticos, una guía de método y diez etapas (R01–R10), desde Cynthiana hasta el epílogo. No fija distancias ni coordenadas; los datos sin cotejo directo permanecen `UNCONFIRMED`.
- La primera etapa de identidad visual quedó incorporada en [`IDENTIDAD_VISUAL.md`](IDENTIDAD_VISUAL.md): tema común de tinta, papel y selección rojo oscuro para `dialog`, menú principal renovado y retrato monocromo original de Rick Grimes en su ficha. El menú quedó confirmado en Debian; falta revisar la ficha de Rick y armonizar THE REFUGE.
- En los selectores de Personajes y Antagonistas el nombre queda limpio y la columna de detalle muestra el tomo/arco de debut junto con la primera y última aparición confirmadas. El intervalo marca los extremos, no una aparición continua; los datos pendientes conservan `UNCONFIRMED`.
- El propietario revisó el elenco contra el cómic. Se quitaron las fuentes de localización y se simplificaron los campos de agrupación; los números, escenas y datos que el cómic no establece no se inventaron.
- El índice de personajes incluye arco, primera y última aparición. Las primeras 60 fichas de `PERSONAJE` (páginas 1 y 2 del selector) quedaron cotejadas por el propietario; los registros restantes conservan `UNCONFIRMED` donde todavía falta una referencia.
- Los selectores de Personajes y Antagonistas muestran el nombre y, al lado, el tomo/arco de debut con los extremos de aparición confirmados; ya no muestran etiquetas de nivel de detalle.
- Se corrigieron nombres que provenían de la adaptación televisiva: el archivo usa Maggie Greene, Carol y Sophia Grimes en el epílogo. El cómic no establece para Carol el apellido Peletier.
- El usuario confirmó que el paquete de personajes 0.5 se aplicó correctamente. Después detectó que THE REFUGE seguía con una versión anterior; la corrección del juego está preparada en este repositorio y requiere una nueva sincronización.
- No se incluyen páginas, paneles ni archivos de cómics protegidos.

### Registro visual — 10 de noviembre de 2026, 20:41 ART

- La captura de Debian confirmó Alexandria OS 0.5 y mostró la paleta azul predeterminada de `dialog`.
- Se añadió config/dialogrc, se conectó desde el lanzador y los comandos personalizados, se renovó el menú principal y se agregó un retrato monocromo original para la ficha de Rick.
- Se actualizó el manual y la guía visual. La VM todavía debe recibir este paquete y revisarse en pantalla; el módulo THE REFUGE queda pendiente de armonización.

### Registro de corrección — 10 de noviembre de 2026, 20:50 ART

- La nueva captura mostró que el menú devolvía al usuario a la consola después de aplicar el tema.
- El instalador ahora genera la configuración de colores desde la versión de dialog instalada en Debian y el lanzador usa el tema predeterminado si la configuración personalizada no pasa la comprobación.
- Se ajustó el menú para usar tamaño automático y se regeneró el paquete de reparación. Falta aplicarlo y confirmar visualmente el resultado en la VM.

### Comprobación visual en Debian — 10 de noviembre de 2026, 20:53 ART

- La captura del propietario muestra Alexandria OS 0.5 con el menú principal abierto: fondo negro, panel claro y selección rojo oscuro.
- El propietario confirmó que le gusta el nuevo menú.
- Pendiente: abrir la ficha de Rick para comprobar el retrato y armonizar THE REFUGE con el mismo lenguaje visual.

### Revisión de contenido de personajes — 10 de noviembre de 2026, 21:23 ART

- La revisión de las primeras dos páginas encontró que 46 de las 60 fichas habían quedado sin su relato y conservaban texto de plantilla. Se recuperó la información narrativa de la fuente del proyecto; otras 13 ya tenían contenido sustantivo y se mantuvieron. Gloria solo tenía una frase de plantilla, así que recibió un registro nuevo basado en sus apariciones identificables.
- Se revisaron las 60 fichas únicas: todas existen, incluyen relato y referencia primaria, están marcadas `CONFIRMED` y coinciden con el arco y los extremos de aparición del índice. No quedaron avisos de borrador ni `UNCONFIRMED` en esas páginas. La comprobación fue estática; la VM todavía necesita recibir este paquete.
- Otis conserva su historia y los eventos relevantes de los números #9, #19-#21 y #34-#35.
- Se corrigió la ficha de Megan: ahora separa la novela *The Road to Woodbury* y el especial *The Governor Special* de la serie regular, y su final queda como aparece en la novela. Su índice sigue indicando que no tiene apariciones en los números regulares ni en el epílogo.
- No se encontró otra pérdida de relatos fuera de las primeras dos páginas al comparar las fichas del repositorio con la fuente anterior.

### Presentación del archivo de personajes — 10 de noviembre de 2026, 21:39 ART

- Los selectores de Personajes y Antagonistas ahora muestran el nombre sin etiquetas de nivel ni agrupación. La columna de detalle muestra el tomo/arco de debut y los números de primera y última aparición disponibles; los datos no confirmados siguen indicados como tales.
- Se simplificó también la descripción de Caminantes identificados en el menú de WALKER DATABASE.
- `NIVEL` se mantiene solo como dato interno para el formato de las fichas y los retratos. Se actualizaron también las instrucciones y la documentación vigente.
- La revisión del cambio fue estática en el código; la aplicación en Debian quedó confirmada por el propietario el 11 de noviembre.
- Se reconstruyó el paquete de sincronización 0.5 con el selector actualizado y las 60 fichas cotejadas; la comprobación de archivos no encontró diferencias ni datos personales excluidos.

### Sincronización confirmada en Debian — 11 de noviembre de 2026, 01:58 ART

- El propietario confirmó que la actualización del archivo de personajes se aplicó correctamente en Debian.
- La terminal informó que se creó un respaldo y que `data/cuaderno.txt` e `imports/` se conservaron. Los avisos sobre metadatos `SCHILY.fflags` no impidieron la instalación.

### Campaña extendida y minijuegos de THE REFUGE — 11 de noviembre de 2026, 05:16 ART

- La campaña ahora ofrece diez decisiones de preparación y ocho turnos de guerra: 18 decisiones estratégicas antes de la confrontación final. Cada jornada consume comida y agua; en los turnos de guerra se duplica el gasto. Las nuevas opciones de preparación permiten reabastecerse, intercambiar suministros, instalar trampas, entrenar a la guardia o atender heridos.
- Se añadieron pruebas opcionales en expediciones, durante una brecha del perímetro y en operaciones de guerra. Incluyen recordar una ruta de flechas, decodificar al revés una clave de radio y responder a señales de ataque; los aciertos suman provisiones o preparación y omitir/fallar no elimina las recompensas ya obtenidas.
- Se mantiene la arena final de una oleada de 40 segundos, con dos vidas, refuerzos cada 2,5 segundos y aceleración leve de los enemigos.
- Archivos afectados: `src/refuge/refuge.py` y `README.md`. Falta sincronizar el paquete incremental en Debian y revisar allí la experiencia de juego.
- Revisión estática de progresión, costos, recompensas y compatibilidad con partidas guardadas; no se ejecutó la aplicación en la VM.

### Ajustes de lectura y prueba final de THE REFUGE — 11 de noviembre de 2026, 04:37 ART

- Los menús de decisiones ahora aprovechan el ancho disponible del terminal y presentan efectos y porcentajes en un formato más compacto, con una leyenda de abreviaturas para evitar que se corten las opciones.
- Antes de iniciar la confrontación final aparece una advertencia con controles, duración y vidas; se puede volver a la elección sin resolverla todavía.
- La prueba acepta flechas y W/A/S/D. Mantiene cuatro oleadas en 22 segundos; ahora hay dos vidas, enemigos más rápidos y refuerzos más frecuentes.
- Archivos afectados: src/refuge/refuge.py y README.md. El paquete incremental queda pendiente de aplicar y revisar visualmente en Debian.
- Validación: revisión estática del código y del contenido empaquetado; no se ejecutó la prueba en la VM.
### Corrección del actualizador 0.6 — 11 de noviembre de 2026, 04:21 ART

- La primera ejecución en Debian copió los archivos, pero el control final del actualizador todavía esperaba la versión 0.5. El script no realiza una restauración automática; el propietario confirmó después que el lanzador quedó en 0.6.
- Se corrigió el actualizador del paquete: ahora acepta una instalación de origen 0.5 o 0.6, valida que el lanzador termine en 0.6 y nombra el respaldo como pre-0.6.
- El propietario confirmó que el lanzador instalado muestra 0.6; no fue necesario volver a aplicar el paquete corregido.
### Preparación de Alexandria OS 0.6 — fichas de las páginas 3 y 4, 11 de noviembre de 2026, 04:05 ART

- Se incorporaron las 56 fichas entregadas por el propietario en twd fichas pag 3-4.rar; las 56 se recibieron marcadas como CONFIRMED.
- Se reemplazaron los expedientes correspondientes y se completaron en el índice sus arcos y extremos de aparición a partir de las referencias primarias consignadas en las fichas. Los datos de apariciones póstumas, menciones y material especial se mantienen distinguidos en cada expediente.
- Se actualizó a 0.6 la versión que muestran el lanzador y el manual. El paquete combina estos cambios con las 14 fichas de caminantes de la actualización anterior y con las correcciones de THE REFUGE ya preparadas.
- Archivos afectados: 56 fichas, data/world/personajes_index.tsv, bin/alexandria, docs/manual_ayuda.txt y README.md.
- Validación estática: las 56 fichas están marcadas CONFIRMED, cada una corresponde a un destino único y el índice recibió sus arcos y números. El propietario confirmó después que el lanzador instalado muestra 0.6.
### Fichas de caminantes identificados — 11 de noviembre de 2026, 03:35 ART

- Se incorporaron las 14 fichas entregadas por el propietario en walkers fichas.rar. Por indicación del propietario, su información se registra como evidencia confirmada; las propias fichas mantienen separadas las notas que identifican como material complementario no canónico.
- Se reemplazaron los perfiles abreviados de data/world/personajes/ por el contenido completo. En data/world/personajes_index.tsv se completaron arcos y extremos de aparición para las 14 entradas.
- Eddie, Justin y Max figuran desde #30 hasta #35; sus fichas distinguen que el desenlace de #35 ocurre fuera de panel. Para las apariciones de un solo número, el selector muestra el número una sola vez.
- Archivos afectados: 14 fichas de caminantes, data/world/personajes_index.tsv, src/world/personajes.sh, README.md.
- Validación estática: se comprobó la correspondencia de las 14 fichas con sus filas y que el índice ya no marque estas entradas como UNCONFIRMED. El paquete preparado aún requiere aplicación y comprobación visual en Debian.
### Corrección de THE REFUGE — 11 de noviembre de 2026, 02:10 ART

- Se detectó que el paquete anterior llevaba una copia vieja del módulo: no incluía el menú de desenlaces y epílogos ni las mejoras posteriores de la prueba final.
- Se recuperaron las crónicas específicas de cada desenlace, la opción para volver a leerlas y la generación del epílogo en partidas ya guardadas que todavía no lo tenían, sin reiniciar la campaña.
- La confrontación final ahora usa el diseño previsto de 40×14, cuatro oleadas en 22 segundos y probabilidades de éxito/fallo para la decisión final. El paquete corregido aún debe aplicarse en Debian.
- Se corrigió el mensaje de victoria de la arena para que también indique cuatro oleadas.
- Se reconstruyó `alexandria-os-debian-sync-0.5.tar.gz` en formato ustar; incluye el módulo actualizado y las fichas restauradas.
- **Validación:** revisión estática del código y contenido del paquete; no se ejecutó el juego en la VM.

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

En los menús, usá las flechas y Enter. Escape cancela o vuelve al menú anterior. El archivo de Personajes muestra hasta 30 fichas por página; elegí `<< Página anterior` o `Siguiente página >>` para cambiar de página. Dentro de cada página podés desplazarte con las flechas y las teclas de página.

Algunos módulos del paquete todavía usan `/home/walker/alexandria-os` o `$HOME/alexandria-os`; mantené esa ruta o actualizá los scripts que la usan.

## Comandos personalizados

El proyecto incluye funciones Bash para abrir sus secciones desde cualquier directorio de la terminal:

- `alexandria`: abre el menú principal.
- `comicarchive`: abre el menú de THE COMIC ARCHIVE.
- `leertomo`: abre directamente el selector de archivos PDF del lector. Los PDF personales deben estar en `imports/comics/`. Durante la lectura, `n` avanza, `p` retrocede y `q` sale.
- `mundo` (también `theworld`), `recorridorick`, `personajes`, `antagonistas`, `animales`, `caminantes`, `comunidades`, `ubicaciones`, `glosario`, `cronologia` y `observaciones`: abren la sección indicada de THE WORLD.
- `refugio` y `cuaderno`: abren THE REFUGE y el cuaderno de campo.
- `fichapersonaje "Nombre exacto"` y `fichaantagonista "Nombre exacto"`: abren una ficha directamente, por ejemplo `fichapersonaje "Rick Grimes"` o `fichaantagonista "Negan"`.
- Atajos para fichas destacadas: `rick`, `carl`, `lori`, `lorigrimes`, `michonne`, `glenn`, `maggie`, `carol`, `dale`, `andrea`, `ezequiel`, `eugene`, `abraham`, `negan`, `shane`, `alpha`, `beta` y `gobernador`.
- `comandosalexandria`: muestra esta lista en la terminal.

En Debian, desde la cuenta normal y con el proyecto en `$HOME/alexandria-os`, instalalas así:

```bash
bash "$HOME/alexandria-os/bin/instalar-comandos"
source "$HOME/.bashrc"
```

El instalador agrega una referencia a `config/comandos.bash` en `~/.bashrc`; no reemplaza el resto de ese archivo ni requiere `sudo`. Las funciones quedan definidas en `config/comandos.bash`. `leertomo` requiere `dialog`, `pdfinfo`, `pdftoppm` y `chafa`, incluidos en las dependencias de instalación indicadas arriba.

La opción **MANUAL / AYUDA** del menú principal abre [`docs/manual_ayuda.txt`](docs/manual_ayuda.txt), una guía desplazable con la navegación, las secciones, la lectura de PDF y los comandos personalizados.

## THE REFUGE

El menú principal abre `src/refuge/refuge.py` desde la opción **THE REFUGE**. La campaña incluye cinco etapas iniciales, cinco jornadas de preparación, ocho turnos de guerra y una decisión final: 18 decisiones estratégicas antes del desenlace. Cada jornada consume comida y agua; durante la guerra se gastan dos raciones de cada una por turno. En la preparación se puede reponer comida y agua, intercambiar suministros, instalar trampas, entrenar a la guardia o atender a los heridos; las opciones cambian según las reservas disponibles. Cada decisión muestra sus probabilidades de éxito y fallo; las elecciones alteran suministros, supervivientes, moral, defensas, inteligencia, alianzas y el desenlace.

Las expediciones, la defensa del perímetro y algunas salidas durante la guerra pueden ofrecer minijuegos opcionales: memorizar una ruta, decodificar al revés una clave de radio o responder rápidamente a señales de ataque. Se controlan con flechas, W/A/S/D o números. El acierto suma suministros o preparación; omitir o fallar la prueba conserva el resultado ya obtenido.

En la confrontación final, la prueba de reflejos se juega en una arena ASCII de 40×14 durante una oleada de 40 segundos. El jugador es `@`; los enemigos son `S` (Salvador), `N` (Negan) y `Z` (caminante). `#` marca obstáculos y `!` avisa un ataque inminente. Movete con las flechas o W, A, S y D; hay dos vidas y Q termina la prueba. Llegan refuerzos cada 2,5 segundos y los enemigos aumentan levemente su velocidad con el tiempo. Cada ataque esquivado suma 2 puntos, hasta un máximo de 6. Antes de iniciar aparece una advertencia con instrucciones y opción para volver a la elección. La decisión final también muestra sus probabilidades de éxito y fallo. La pantalla usa texto en la terminal, sin interfaz gráfica.

Cada desenlace tiene una crónica propia disponible desde **Leer desenlace y epílogo**. Si una partida guardada de una versión anterior carece de epílogo, el módulo lo genera al abrir ese cierre y conserva el resto del registro.

La campaña se guarda localmente como JSON en `$XDG_STATE_HOME/alexandria-os/the-refuge.json`; si `XDG_STATE_HOME` no está definido, usa `~/.local/state/alexandria-os/the-refuge.json`. Los datos guardados no se escriben en el repositorio.

La historia presenta una variación original inspirada en el arco *All-Out War*. Image Comics identifica el número [#115](https://imagecomics.com/comics/releases/the-walking-dead-115) como su inicio y el [#126](https://imagecomics.com/comics/releases/the-walking-dead-126) como su conclusión. Los valores, decisiones y finales de la campaña son mecánicas de juego y no alteran el canon.

**Validación:** los cambios de campaña se revisaron estáticamente; falta aplicar el paquete y observar los minijuegos, la arena y los epílogos en la VM Debian.

## Archivo de personajes

`data/world/personajes_index.tsv` conecta cada entrada con su archivo, categoría, agrupación, nivel interno y datos confirmados de primera y última aparición. `src/world/personajes.sh` carga el índice para personajes, antagonistas, caminantes y animales. Los perfiles se guardan en `data/world/personajes/` y en los demás archivos de `data/world/`. En los selectores de personajes, cada nombre se acompaña por el tomo/arco de debut y el rango entre primera y última aparición cuando está confirmado.

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

### 2026-11-09 16:53 ART — Recorrido de Rick

- Se conectó `Recorrido de Rick` al menú de `THE WORLD` mediante `src/world/menu.sh` y el selector `src/world/recorrido_rick.sh`. El índice `data/world/recorrido_rick_index.tsv` reúne 14 entradas: tres mapas esquemáticos, una guía de método y diez etapas (R01–R10).
- Los mapas cubren el origen y los refugios del sur, la red de comunidades y el tramo final. Las diez etapas recorren los números #1–193 y el epílogo.
- Los mapas no asignan escalas, carreteras, distancias ni coordenadas. Las fichas usan rangos como localizadores y conservan `UNCONFIRMED` hasta el cotejo directo de números y escenas. Pittsburgh permanece sin conexión geográfica afirmada; Oceanside sigue fuera del mapa mientras falte confirmación en el canon del cómic, y la ubicación de la granja del epílogo queda abierta.
- **Pendiente:** probar el selector y los textos en la VM Debian y cotejar las etapas con los ejemplares. La revisión de esta tarea fue estática y no valida la ejecución en la VM.

### 2026-11-09 22:38 ART — Reglas de entrega académica

- Se actualizó `AGENTS.md` con las consignas del proyecto final: imagen `.ova` de Debian usable y sin entorno gráfico, e informe final exclusivamente en PDF.
- Se añadió una lista de contenidos del informe, documentación de archivos de sistema editados, aplicaciones propias, tecnologías, manual, comandos y alias, y evidencia para que el docente pueda acceder y probar el sistema.
- Las reglas exigen informar las credenciales en el PDF privado de entrega, pero prohíben guardar o pedir contraseñas reales en chats, Git o capturas; los borradores usan campos para que el propietario los complete localmente.
- **Validación:** se cotejó `AGENTS.md` con las consignas recibidas. No se generó ni se validó todavía el `.ova` o el informe final.


### 2026-11-09 17:24 ART — Corrección de la continuación en THE REFUGE

- El reporte indicó que la aplicación se cerraba al continuar la partida en la confrontación final. La revisión de `src/refuge/refuge.py` localizó la causa: `final_decision()` entregaba opciones de tres valores, pero `choose()` esperaba pares de etiqueta y descripción. El desempaquetado fallaba al construir el menú.
- Se corrigió el formato de las opciones y se conservaron sus ayudas dentro de las descripciones. La lógica de desenlaces y el guardado no se modificaron.
- **Validación:** revisión estática del código en `main`; todavía no ejecutado en la VM Debian.
- **Pendiente:** sincronizar `src/refuge/refuge.py` con Debian y reanudar la partida guardada en `CONFRONTACIÓN FINAL` para elegir un desenlace y confirmar que queda guardado como finalizado.

### 2026-11-09 18:06 ART — Prueba de reflejos en THE REFUGE

- Se incorporó a la confrontación final una secuencia textual de tres señales aleatorias (W, A, S o D), con 2,5 segundos por señal y respuesta directa de tecla, sin Enter. Cada acierto añade 2 puntos al puntaje del desenlace.
- El resultado registra los aciertos de reflejos y el puntaje junto con el desenlace. El modo de terminal se restaura al terminar la secuencia.
- **Validación:** revisión estática del código en `main`; no se ejecutó el QTE en Debian. El usuario confirmó que la campaña alcanza un desenlace.
- **Pendiente:** sincronizar la actualización en la VM Debian y comprobar aciertos, errores, tiempo agotado, puntaje final y que el terminal queda usable al salir.

### 2026-11-09 22:42 ART — Arena de esquiva de THE REFUGE

- La prueba de reflejos pasó de tres señales aisladas a una arena ASCII de tres oleadas durante 18 segundos. El jugador se mueve con WASD; aparecen Salvadores, Negan y caminantes, con obstáculos y avisos de ataque.
- La arena tiene tres vidas; Q permite terminarla. Cada ataque anunciado que se esquiva añade 2 puntos al desenlace, con un máximo de 6. La lógica restaura el modo previo de la terminal al salir.
- **Validación:** revisión estática del código en `main`; la arena no se ejecutó en Debian. El usuario había confirmado el desenlace de la campaña antes de este cambio.
- **Pendiente:** sincronizar la actualización en la VM Debian y comprobar movimiento, avisos, daño, puntaje, desenlace guardado y estado de la terminal al salir.

### 2026-11-09 23:00 ART — Comandos personalizados de terminal

- Se añadieron las funciones `alexandria`, `comicarchive` y `leertomo`, definidas en `config/comandos.bash`.
- `leertomo` abre directamente el selector del lector PDF; el lector y el menú de la biblioteca resuelven la carpeta desde `ALEXANDRIA_ROOT`, con `$HOME/alexandria-os` como valor predeterminado.
- Se agregó `bin/instalar-comandos`, que incorpora una referencia marcada a `~/.bashrc` sin reemplazar su contenido y puede ejecutarse de nuevo sin duplicar el bloque.
- **Validación:** revisión estática de los cambios. No se ejecutaron en la VM Debian.
- **Pendiente:** copiar estos archivos a la VM, instalar las funciones para la cuenta normal y comprobar los tres comandos; para `leertomo`, probar con un PDF autorizado en `imports/comics/`.

### 2026-11-09 23:14 ART — Accesos directos a THE WORLD

- Se ampliaron los comandos personalizados para abrir directamente las secciones de THE WORLD, THE REFUGE y el cuaderno de campo.
- Se añadieron `fichapersonaje` y `fichaantagonista`, que abren una ficha por nombre exacto sin pasar por el selector. Se incorporaron atajos para Rick, Carl, Michonne, Glenn, Maggie, Andrea, Ezekiel, Negan y el Gobernador.
- `comandosalexandria` muestra las opciones disponibles desde la terminal; también se incluyeron atajos para Carol, Dale, Lori, Eugene, Abraham, Shane, Alpha y Beta.
- `src/world/personajes.sh` ahora acepta opcionalmente el nombre exacto de una ficha; conserva su presentación, retrato y retorno con Escape.
- **Validación:** revisión estática del flujo y de los nombres presentes en el índice. No se ejecutaron los comandos en Debian.
- **Pendiente:** copiar la actualización a la VM y probar accesos directos a secciones y fichas.

### 2026-11-09 23:21 ART — Manual de ayuda integrado

- La opción **MANUAL / AYUDA** del menú principal ahora abre `docs/manual_ayuda.txt` en una vista desplazable.
- El manual explica la navegación, las secciones, el lector PDF, la instalación de comandos Bash, los accesos directos a categorías y fichas, y las dependencias de `leertomo`.
- Se fijaron finales LF para el lanzador sin extensión, el instalador de comandos y las funciones `.bash`, para evitar reintroducir finales CRLF en Windows.
- **Validación:** revisión estática del cambio; no se abrió el manual en la VM Debian.
- **Pendiente:** copiar el lanzador y el manual actualizado a la VM y recorrerlos desde el menú principal.

### 2026-11-09 23:43 ART — Limpieza de fichas del elenco

- A pedido del propietario, quien indicó haber cotejado todas las fichas del elenco, se actualizó el material de `data/world/personajes/` y los expedientes vinculados desde `personajes_index.tsv`.
- En 215 fichas breves, `UNCONFIRMED` pasó a `CONFIRMED`, se eliminó el bloque `FUENTE DE LOCALIZACIÓN`, se retiró el texto de revisión pendiente y `AGRUPACIÓN EN LA LISTA DE REFERENCIA` se simplificó a `AGRUPACIÓN`.
- En 18 expedientes ampliados, las notas sobre datos que la serie no establece se rotularon `NO ESTABLECIDO EN EL CÓMIC`, sin alterar esos datos ausentes.
- **Validación:** revisión estática de las fichas afectadas; no se comprobó la presentación en Debian. El índice conserva `UNCONFIRMED` solo para los valores de arco y primera aparición que no tienen localizador registrado.
- **Pendiente:** copiar las fichas actualizadas a la VM y revisar una ficha breve y un expediente ampliado.

### 2026-11-09 23:57 ART — Pulido del nombre y la versión

- Se corrigió el título de `ALEXANDIRA OS 0.1` a `ALEXANDRIA OS 0.2` en el lanzador principal.
- Se actualizó a 0.2 la cabecera del manual de ayuda y la versión descrita en este README.
- **Validación:** búsqueda estática de los rótulos de versión y revisión del diff; no se comprobó la pantalla en Debian.
- **Pendiente:** copiar el lanzador y el manual actualizados a la VM y revisar el título en pantalla.

### 2026-11-09 23:59 ART — Confirmación visual de Alexandria OS 0.2

- El usuario confirmó en Debian, mediante una captura, que Alexandria OS abre el menú principal y muestra correctamente el nombre `ALEXANDRIA OS 0.2`.
- **Alcance:** queda comprobado el arranque del menú principal y su rótulo; la captura no verifica por sí sola las demás secciones.
- **Pendiente:** probar las fichas y categorías de THE WORLD en esta versión.

### 2026-11-10 00:27 ART — Paginación del archivo de personajes

- El selector de personajes ahora divide los resultados en páginas de hasta 30 fichas e incluye opciones para ir a la página anterior o siguiente.
- Al abrir una ficha, el selector vuelve a la misma página y conserva la selección. Las categorías con menos de 30 entradas quedan en una sola página.
- Se actualizó el manual de ayuda con la navegación por páginas.
- **Validación:** revisión estática del flujo; no se ejecutó en Debian.
- **Pendiente:** copiar el selector y el manual actualizados a la VM y recorrer las páginas desde THE WORLD.

### 2026-11-10 00:35 ART — Confirmación de la paginación en Debian

- El usuario confirmó que la navegación paginada del archivo de personajes funciona correctamente en Debian.
- **Alcance:** queda confirmada por el usuario la función probada; no se infieren validaciones de otras categorías.

Al cerrar cada tarea, agregá una entrada cronológica a este historial sin borrar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.

### 2026-11-10 — Matriz manual para la versión 0.4

- **Trabajo realizado:** creación de [la matriz de pruebas manuales](docs/MATRIZ_PRUEBAS_MANUALES_0.4.md), ordenada por módulo, con pasos, resultados esperados, criterios y campos para fecha, hora ART y evidencia; incluye 46 registros individuales para las fichas provisionales.
- **Base consultada:** GitHub `main`, commit `84544ac3aa3d0dafe58e1babf3524aacd16c6a20`, que incluye la ampliación `d6be6a17dae73dba103ce741f81c98f6f868cead` y la primera aplicación monocromática posterior. Esta copia local conserva documentación anterior; esta entrada no afirma que el código local o la VM estén sincronizados.
- **Validación documental:** inspección del README, reglas, árbol, lanzador y módulos remotos. Las confirmaciones históricas se separaron de las pruebas pendientes; no se ejecutó ninguna prueba en Debian ni se cotejó el canon en esta tarea.
- **Pendientes:** sincronizar e identificar la revisión en la VM, ejecutar y registrar cada caso; mantener `UNCONFIRMED` para afirmaciones sin cotejo primario. Los cambios documentales de esta tarea quedan locales, sin publicación.

### 2026-11-10 19:11 ART — Corrección de las páginas 1 y 2 de Personajes

- Se corrigieron las primeras 60 fichas `PERSONAJE`: estado de evidencia, arco, primera aparición, última aparición y alcance individual. Otis queda en `Miles Behind Us`, con primera aparición en `#9` y última en `#35` como caminante.
- Se añadió `ULTIMA_APARICION` al índice y el selector muestra el rango individual junto al nombre. Los extremos no implican que el personaje aparezca en todos los números intermedios.
- Megan queda identificada como material complementario, sin apariciones en la serie regular.
- **Validación:** comprobación estática del índice y las 60 fichas; no se ejecutó la interfaz en Debian.
- **Pendiente:** revisar visualmente la presentación del selector en Debian.

### 2026-11-10 19:34 ART — Pamela Milton también en Antagonistas

- Pamela se mantiene en Personajes y se agrega también a Antagonistas como antagonista política secundaria durante el conflicto de la Commonwealth. Las dos categorías abren la misma ficha; su arco deja claro que esa función no es permanente.
- El índice tiene 249 asignaciones de categoría y 248 fichas únicas. La ficha de Pamela indica la clasificación adicional.
- **Validación:** comprobación estática de las dos filas de Pamela y de la ruta compartida; no se ejecutó el selector en Debian.

### 2026-11-10 — Preparación de Alexandria OS 0.5

- Se actualizó el rótulo de desarrollo en el lanzador, el manual y el estado del README. La VM observada sigue mostrando 0.4.
- Se conserva como base el conjunto local actualizado de personajes, que agrega el alcance individual, la última aparición y la doble clasificación de Pamela.
- Se preparó un paquete de 412 archivos y un instalador que primero respalda el proyecto Debian; se excluyeron `.git`, `imports/`, `data/cuaderno.txt`, datos de credenciales y carpetas de configuración de Codex. El recurso temporal de VirtualBox es de solo lectura.
- **Validación:** comprobación estática del contenido y las exclusiones del paquete, y de la carpeta temporal configurada en la VM. No se aplicó la actualización ni se probó 0.5 en Debian.
- **Pendiente:** ejecutar el instalador desde Debian, conservar `data/cuaderno.txt` e `imports/` y comprobar el menú y las dos páginas del selector.

### 2026-11-10 — Corrección de visores sin contenido aparente

- **Reporte:** al abrir varias categorías, en especial los apartados de WALKER DATABASE, no se veía el contenido.
- **Diagnóstico estático:** los siete textos de `data/world/walker_database/` existen y tienen contenido. En las copias Debian e integración, `caminantes.sh` y `observaciones.sh` solicitaban cuadros fijos de 28×110; esos cuadros pueden exceder la terminal y el flujo regresaba al menú sin indicar el problema. Las rutas de datos también dependían de `$HOME/alexandria-os` en la copia Debian.
- **Trabajo realizado:** ambos lectores y sus menús ahora dejan que `dialog` ajuste el tamaño (`0 0`); las rutas se resuelven desde el directorio del módulo y un archivo ausente o ilegible muestra su ruta.
- **Archivos afectados:** `src/world/caminantes.sh` y `src/world/observaciones.sh` en `alexandria-os-debian-actual/` y `alexandria-os-integracion-repo/`; se amplió el caso CA-02 y FO-01 de la matriz manual.
- **Validación:** inspección estática de rutas, tamaños de ventana y presencia de los archivos. No se ejecutó en Debian ni se marca ninguna categoría como probada.
- **Pendiente:** sincronizar estos dos módulos en la VM y ejecutar CA-02 y FO-01 en ambos tamaños de terminal anotados en la matriz.

### 2026-11-10 21:40 ART — Primera verificación local de Alexandria OS 0.5

- **Verificado estáticamente:** integridad de los seis índices principales y rutas de sus fichas; 249 asignaciones/248 fichas únicas, sin rutas faltantes, filas mal formadas ni archivos vacíos. Los conteos de Comunidades, Ubicaciones, Glosario, Cronología y Recorrido de Rick coinciden con los índices actuales.
- Los siete textos de WALKER DATABASE y los tres registros de FIELD OBSERVATIONS existen y tienen contenido. Las 46 fichas añadidas en 0.4 están en la copia 0.5, aparecen como `CONFIRMED` con referencia primaria y nota de cotejo, y están dentro de las primeras 60 fichas que el propietario indicó haber revisado. Este registro no es un cotejo independiente de escenas.
- Quedan 527 valores `UNCONFIRMED` en 187 expedientes únicos; se creó [la cola de cotejo primario](docs/cotejo_primario_pendiente_0.5.csv) y el [informe de verificación inicial](docs/VERIFICACION_0.5_INICIAL.md).
- **Alcance:** no se ejecutó Bash/`dialog` ni se marcó como aprobada ninguna prueba manual. La VM observada usa 0.4; el paquete 0.5 disponible contiene los visores antiguos de 28×110 y su instalador exige un 0.5 preexistente. En `imports/comics/` solo hay `.gitkeep`; no se cotejaron hechos narrativos con ejemplares primarios.
- **Pendiente:** regenerar y revisar el paquete 0.5, ejecutar la matriz en Debian y cotejar los campos pendientes cuando estén disponibles los cómics primarios.

### 2026-11-11 01:45 ART — Segunda pasada de verificación

- **Comprobado en Windows:** WSL no está instalado y no hay `bash`/`sh` disponible, así que todavía no se puede ejecutar la interfaz desde esta sesión de PowerShell.
- El paquete nuevo `alexandria-os-0.5-verificacion.tar.gz` incluye los lectores adaptativos y reconoce lanzadores 0.4/0.5, pero el listado del tar marca **cero archivos ejecutables**; los 13 scripts `.sh` no tienen permiso de ejecución. No usarlo para actualizar la VM hasta corregir ese empaquetado.
- La matriz sigue sin ejecuciones: 79 filas `Pendiente`, 0 `Aprobada`. La cola de cotejo conserva 527 valores pendientes y las columnas de evidencia, fecha y hora vacías.
- No hay ejemplares primarios disponibles en `imports/comics/`; los valores `UNCONFIRMED` permanecen sin cambios. No se modificó ningún estado de prueba ni de evidencia narrativa.

### 2026-11-11 02:12 ART — Arreglo aplicado en la copia local

- Los selectores de WALKER DATABASE y FIELD OBSERVATIONS usan dimensiones adaptables; los lectores resuelven sus datos desde la ubicación del proyecto y muestran la ruta si un archivo no puede leerse. Los cambios están en `src/world/caminantes.sh` y `src/world/observaciones.sh` de esta copia de trabajo.
- Se normalizaron `observaciones.sh` y `antagonistas.sh` a LF, de acuerdo con `.gitattributes`; una inspección estática de los 14 scripts y lanzadores Bash ya no encuentra finales CRLF.
- Se corrigieron los permisos del paquete `alexandria-os-0.5-verificacion.tar.gz`: 16 archivos ejecutables y ningún script `.sh` sin ejecución. El paquete contiene el código actual y el instalador reconoce la VM 0.4 para actualizarla a 0.5.
- **Aún pendiente:** ejecutar el paquete y la matriz en Debian. Las 79 pruebas manuales siguen pendientes; no se dio por validada visualmente ninguna categoría.

### 2026-11-11 02:50 ART — Diagnóstico de WALKER DATABASE

- La captura muestra `Anatomía y daño` con el lector abierto pero sin texto. El archivo local contiene 1073 bytes; el paquete también lo incluye. La copia instalada en la VM no se pudo leer por SSH desde esta sesión, así que no se confirma su tamaño.
- La extracción anterior de `tar` falló por archivos ya existentes y cabeceras incompatibles, aunque después el instalador informó que aplicó la actualización. Se regeneró el paquete en formato USTAR, sin `.git` ni cabeceras PAX.
- `caminantes.sh` ahora informa si el archivo no se puede leer o tiene cero bytes. Para aplicar la copia conocida en la VM, se puede transferir directamente el script y toda la carpeta `walker_database` por SCP, sin volver a extraer el tar.
- La matriz conserva las 79 pruebas pendientes; la captura no se marcó como aprobación.

### 2026-11-11 03:10 ART — Normalización de textos del visor

- La prueba mínima ASCII de `dialog` mostró texto, pero `Anatomía y daño` quedó vacío. Los siete archivos de `data/world/walker_database/` y los tres de `data/world/field_observations/` estaban en CRLF en la copia de Windows, aunque `.gitattributes` define LF.
- Los diez archivos se normalizaron a LF. `anatomia_dano.txt` pasa de 1073 a 1048 bytes. Falta sobrescribir la carpeta remota por SCP y volver a abrir categorías; la prueba no se marca como aprobada hasta observar contenido en Debian.

### 2026-11-11 03:13 ART — Primer documento visible en la VM

- El usuario confirma que WALKER DATABASE ya funciona y comparte una captura con el texto de `Anatomía y daño` visible tras la normalización LF.
- Es una observación positiva de ese documento; las otras seis categorías, navegación de retorno y prueba en ambos tamaños siguen pendientes. CA-02 conserva estado `Pendiente` y los estados de evidencia narrativa no cambian.


## Entradas históricas conservadas del repositorio

### 2026-11-09 23:03 ART — Ampliación de campaña y azar en THE REFUGE

- La campaña pasó de seis decisiones previas al final a diez jornadas: se añadieron reconstrucción y recepción de refugiados, y la guerra contra los Salvadores pasó de tres a cinco turnos.
- Se incorporaron incidentes aleatorios que pueden modificar reservas, moral, supervivientes o alianzas, junto con maniobras de riesgo cuya probabilidad mejora con inteligencia y defensas. Dos jornadas consecutivas con faltantes causan una baja; una acción marcada como peligro extremo puede terminar la campaña.
- La partida registra el resultado de cada maniobra y conserva el estado de derrota. La arena ASCII de reflejos sigue en la confrontación final y no se añadió interfaz gráfica.
- **Validación:** revisión estática de `src/refuge/refuge.py` en `main`; no ejecutado en Debian.
- **Pendiente:** sincronizar el módulo y probar una campaña completa, incidentes, riesgos, derrotas, guardado y reanudación en la VM.

### 2026-11-09 23:23 ART — Epílogos narrativos en THE REFUGE

- Al terminar una campaña, THE REFUGE presenta una crónica desplazable que cambia según el desenlace: victoria estratégica, victoria con pérdidas, retirada negociada, evacuación, derrota en la confrontación o derrota anticipada por colapso del refugio.
- La decisión final distingue la ruta de sostener el frente, negociar o evacuar; el puntaje estratégico determina la resolución y la narración describe una posible continuación de esa línea alternativa. Los epílogos quedan guardados y pueden volver a leerse desde el menú.
- La narración se identifica como una variación original del cómic; no modifica el canon. La interfaz sigue en terminal y usa el cuadro de texto desplazable de `dialog`.
- **Validación:** revisión estática del código y del README en `main`; no ejecutado en Debian.
- **Pendiente:** sincronizar el módulo y jugar cada ruta de desenlace y derrota, verificando que el epílogo aparezca al terminar y quede accesible al volver al menú.

### 2026-11-09 23:39 ART — Corrección del acceso a THE REFUGE

- La ejecución directa en Debian mostró un error de sintaxis en la definición de final_decision: faltaba el carácter : al final de la línea.
- Se corrigió la definición en src/refuge/refuge.py. La opción del lanzador sigue conectada al módulo.
- **Validación:** el error reportado queda corregido en GitHub main; la versión corregida todavía no se ejecutó en Debian.
- **Pendiente:** sincronizar el módulo corregido en la VM y confirmar que THE REFUGE abre desde el menú y desde la ejecución directa.

### 2026-11-09 23:45 ART — Confirmación de apertura en Debian

- El usuario confirmó que THE REFUGE abre al ejecutar directamente el módulo corregido desde Debian, después de agregar los dos puntos que faltaban en final_decision.
- **Alcance:** queda confirmada la ejecución directa del módulo. No se registra todavía la entrada desde el menú principal ni la prueba completa de la campaña.
- **Pendiente:** confirmar la apertura desde bin/alexandria y recorrer los desenlaces en Debian.

Al cerrar cada tarea, agregá una entrada cronológica a este historial sin borrar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.

### 2026-11-10 — Versión de desarrollo 0.3

- El lanzador `bin/alexandria` ahora muestra `ALEXANDRIA OS 0.3`; se centralizó el número de versión en una variable para facilitar futuros cambios.
- Se añadió la categoría **¿Qué es THE REFUGE?**. Todas las opciones de campaña y las tres decisiones finales muestran su probabilidad de éxito/fallo y las estadísticas relacionadas. Los fracasos no conceden los beneficios de la opción y conservan costes o penalizaciones.
- La arena pasó de 28 × 9 a 40 × 14, incorporó cobertura adicional, tres enemigos iniciales y cuatro refuerzos (hasta siete en total), cuatro oleadas de 22 segundos y una velocidad enemiga aproximadamente 10 % mayor.
- **Validación:** el cambio quedó registrado en GitHub `main`; la versión 0.3 aún no se ejecutó en Debian. La confirmación previa corresponde al arranque directo de una versión anterior.
- **Pendiente:** sincronizar el lanzador y el módulo en la VM; comprobar el acceso desde el menú principal, las probabilidades y consecuencias, la arena y una campaña completa.

### 2026-11-10 — Versión de desarrollo 0.4

- Se incorporaron descripciones de trabajo del archivo aportado `twd fichas pag 1-2.rar` a 46 fichas existentes en `data/world/personajes/`. No se cambiaron las categorías ni el nivel del índice común.
- Las fichas conservan `UNCONFIRMED`: el material contiene números, escenas, relaciones y destinos que no se cotejaron con el cómic. La verificación primaria queda pendiente.
- `bin/alexandria` y este README ahora indican la versión de desarrollo 0.4.
- **Validación:** se comprobó la correspondencia de las 46 fichas con sus entradas existentes y se registró el cambio en GitHub `main`. No se ejecutó esta versión en Debian ni se verificaron todas las escenas en el cómic.
- **Pendiente:** cotejar cada afirmación con los números primarios y sincronizar/probar la versión 0.4 en la VM Debian.

### 2026-11-10 — Dirección visual monocromática

- Se revisó IDENTIDAD_VISUAL.md para orientar Alexandria OS hacia blanco, negro, grises y tramas diagonales discretas, manteniendo la seriedad de los expedientes.
- La propuesta conserva la interfaz exclusivamente textual. El azul intenso deja de ser parte de la dirección visual; la selección se distinguirá con contraste y video inverso.
- No se cambiaron pantallas ni código en esta tarea. El visor de personajes ya puede representar retratos en la terminal; la paleta y el tratamiento global siguen pendientes de implementación.
- **Validación:** se actualizó la documentación en main; no se ejecutó ni se verificó una nueva interfaz en Debian.
- **Pendiente:** aplicar la propuesta a una ficha y al menú, y revisar su legibilidad y navegación en la VM.

### 2026-11-10 — Primera aplicación de identidad monocromática

- Se añadió `config/dialogrc` con fondo negro, paneles claros y selección en video inverso blanco y negro. `bin/alexandria` exporta DIALOGRC para los módulos abiertos desde el menú principal y agrega una franja de archivo al encabezado.
- `src/world/personajes.sh` usa rayas diagonales en los bordes superior e inferior del marco del retrato; el texto de las fichas no cambia.
- **Validación:** revisión estática de los archivos actualizados en GitHub `main`; el cambio todavía no se ejecutó en Debian.
- **Pendiente:** copiar la actualización a la VM y revisar el menú, una ficha con retrato, la legibilidad y la navegación. La verificación visual queda limitada a las pantallas que se comprueben allí.

### 2026-11-16 21:55 ART — Integración de la base 0.6 y marca del menú

- Se integraron desde el ZIP los módulos de `src/`, lanzadores, configuración, fichas e índices de `data/` y documentación; se conservaron entradas históricas del repositorio. No se copiaron respaldos, importaciones ni retratos sin procedencia verificada.
- `bin/alexandria` incorpora ALEXANDRIA/molino/SAFE ZONE en rojo y negro, sin TWD. Se actualizaron `IDENTIDAD_VISUAL.md`, el manual, `.gitignore` y las dos reglas de esquema de `AGENTS.md` que corresponden al índice integrado.
- **Validación en nube Debian 13.6:** sintaxis de 15 scripts Bash y AST de Python; seis índices íntegros; `tests/smoke_terminal.py` aprobó 80×24 y 120×40, incluida la apertura de ayuda, THE WORLD y THE REFUGE y salida a consola. `git diff --check` sin errores. Se repitió la instalación local de herramientas y se guardaron `install_script` y `start_skill` en el borrador del entorno.
- **Pendientes:** se conservan las 79 pruebas manuales y los resultados documentados sin aprobar casos nuevos de esa matriz; no se probaron campaña completa, canon, OVA ni PDF. Publicación del entorno y validación en una tarea nueva pendientes. Alcance completo en [Continuación 0.6](docs/CONTINUACION_0.6.md).

### 2026-11-16 22:14 ART — Logo aprobado en el menú principal

- Se integró el logo PNG aprobado en `assets/logo-alexandria-safe-zone.png` y se sustituyó la marca de caracteres por una pantalla principal en `src/ui/main_menu.py`: Chafa dibuja el PNG a la izquierda y la navegación de teclado ocupa el panel derecho.
- El layout usa 40×20 celdas para la imagen en 80×24 y 60×30 en 120×40; la imagen mantiene su proporción.
- **Comprobación realizada:** `python3 tests/smoke_terminal.py` pasó en ambos tamaños con Bash, Python, Chafa y el menú real bajo pseudoterminal. Comprobó celdas de imagen, ubicación y legibilidad del menú, seis opciones, ayuda, acceso a THE WORLD y THE REFUGE, y salida. No es inspección visual en VirtualBox ni ejecución de la matriz manual.
- Las 79 pruebas manuales siguen pendientes. No se creó una OVA ni un PDF; Git los mantiene ignorados.

### 2026-11-16 22:28 ART — Revisión del logo y la documentación 0.6

- Se leyó `AGENTS.md` y se revisaron README, guía visual, manual y bitácora. Ya documentaban el PNG aprobado, la posición junto al menú, Chafa/curses y las dimensiones previstas. En la guía visual, una frase todavía llamaba “actual” a la marca textual inicial; se corrigió para dejar claro que es histórica y que el PNG la reemplazó.
- El PNG está en `assets/logo-alexandria-safe-zone.png`, aparece en el checkout como archivo nuevo sin seguimiento y el lanzador lo pasa a `src/ui/main_menu.py`. No se ejecutó el menú ni se corrieron pruebas en esta revisión.
- La matriz manual coincide byte por byte con la copia del ZIP adjunto; las 79 pruebas quedan pendientes y no se alteró su contenido ni sus resultados históricos.
- El estado del checkout contiene 314 rutas modificadas ya versionadas y 20 nuevas sin seguimiento, sin cambios staged. Los archivos PDF y OVA no están rastreados y sus extensiones siguen ignoradas. No se hizo commit, push, PR ni publicación del entorno.


### 2026-11-16 — Matriz manual alineada con Alexandria OS 0.6

- El propietario confirmó que todas las pruebas manuales de 0.4 estaban aprobadas. La matriz histórica registra esa confirmación, pero no se proporcionaron la fecha original, el commit, el entorno ni evidencias individuales.
- Se agregó [la matriz de regresión 0.6](docs/MATRIZ_PRUEBAS_MANUALES_0.6.md), con las expectativas actuales del menú con logo, el índice y sus conteos, los módulos y las verificaciones separadas de OVA/PDF. Sus pruebas siguen pendientes de ejecución en la VM de entrega.
- El estado funcional no modifica etiquetas narrativas. No se ejecutaron pruebas ni se validó la VM en esta actualización documental.
