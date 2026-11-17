# Alexandria OS

**Versión de la imagen de entrega: 0.6.** Sistema base: Debian GNU/Linux 13 (Trixie), amd64.

Alexandria OS es un entorno de archivo y consulta basado en Debian 13 para el cómic principal de *The Walking Dead*, una biblioteca personal y módulos de supervivencia.

Repositorio privado y fuente de verdad: [thiagoalfonsounp-creator/alexandria-os](https://github.com/thiagoalfonsounp-creator/alexandria-os).

## Estado de la entrega — 17 de noviembre de 2026

Preparé Alexandria OS 0.6 sobre Debian GNU/Linux 13 (Trixie), amd64, con una interfaz de terminal en español. La entrega incluye la imagen virtual `.ova` y el informe final en PDF.

Importé la OVA en VirtualBox, inicié sesión y recorrí **THE WORLD**, **THE COMIC ARCHIVE** y **THE REFUGE**.

- El menú principal tiene seis secciones: THE WORLD, THE COMIC ARCHIVE, THE REFUGE, Cuaderno de campo, Manual / Ayuda y Terminal.
- **THE WORLD** reúne 248 fichas únicas en 249 asignaciones: 225 personajes, 6 antagonistas, 14 caminantes y 4 animales. Incluye además Comunidades (13 fichas), Ubicaciones (19), Glosario (40 términos y guía), Cronología (33 etapas y guía), Observaciones (13 fichas) y Recorrido de Rick (14 documentos).
- **THE COMIC ARCHIVE** organiza archivos PDF y CBZ personales o autorizados. El lector incluido abre tomos en PDF. No se distribuyen cómics protegidos.
- **THE REFUGE** es una campaña de decisiones con recursos persistentes, guardado JSON, minijuegos opcionales, un QTE de horda y una arena ASCII.
- La interfaz es de terminal y no incluye entorno gráfico. El menú y las instrucciones están en español rioplatense.
- La matriz manual de cierre registra 44 casos: 33 aprobados, 11 pendientes y 0 fallidos. Los pendientes siguen señalados en la matriz.
- El informe PDF reúne la guía de uso y evaluación, las aplicaciones, los cambios de configuración, las capturas y el enlace directo a la OVA.

## Instalación y ejecución

La interfaz usa Bash y `dialog`; THE REFUGE se ejecuta con Python 3. Para el lector PDF y las funciones de imagen se usan `poppler-utils` y `chafa`.

```bash
sudo apt update
sudo apt install bash dialog nano unzip zip poppler-utils chafa python3 less file curl
```

Desde la raíz del proyecto:

```bash
./bin/alexandria
```

En los menús, usá las flechas y Enter. Escape cancela o vuelve al menú anterior. El selector de personajes se desplaza con las flechas y las teclas de página.

Algunos módulos del paquete todavía usan `/home/walker/alexandria-os` o `$HOME/alexandria-os`; mantené esa ruta o actualizá los scripts que la usan.

## THE REFUGE

Abrí el módulo desde la opción **THE REFUGE** del menú principal. También podés ejecutarlo directamente con:

```bash
python3 src/refuge/refuge.py
```

La campaña de la versión 0.6 combina cinco etapas iniciales, cinco jornadas de preparación, ocho turnos de guerra y una decisión final. Las elecciones afectan los recursos y el estado del refugio. Incluye guardado local en JSON, minijuegos opcionales, un QTE durante el evento de horda y una arena ASCII en la confrontación final.

El juego guarda la partida en `$XDG_STATE_HOME/alexandria-os/the-refuge.json`; si esa variable no existe, usa `~/.local/state/alexandria-os/the-refuge.json`. Los finales son variaciones originales inspiradas en el cómic y no cambian su canon.

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
src/refuge/             Campaña de supervivencia y epílogos en terminal
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
- En Debian probé `WALKER DATABASE` y `FIELD OBSERVATIONS`; ambas opciones abrieron correctamente.

### 2026-11-07 — Ampliación del archivo de personajes

- Se recuperó el inventario agrupado de personajes y se integraron 248 entradas en `personajes_index.tsv`, con fichas vinculadas a todas las rutas.
- Se separaron personajes, antagonistas principales, animales y caminantes identificados en los menús. Cada nombre muestra su arco y número de primera aparición cuando están confirmados; los datos pendientes conservan `UNCONFIRMED`.
- Se ampliaron expedientes de personajes principales y se añadieron fichas breves para secundarios. Las entradas sin verificación directa conservan `UNCONFIRMED` y no reciben números de edición inventados.
- Se ajustaron nombres y continuidad al cómic principal, y se documentaron los materiales complementarios que quedan fuera del selector.
- El código nuevo requiere comprobación en la VM Debian; la ejecución anterior no verifica esta ampliación.


### 2026-11-07 — Integración de la copia Debian con el índice de personajes

- La copia actual de Debian contiene 13 fichas de Comunidades, 19 de Ubicaciones, 41 entradas de Glosario y 34 etapas de Cronología. La rama `main` contiene el índice común de 248 fichas: 225 personajes, 5 antagonistas, 14 caminantes y 4 animales.
- La integración conecta Personajes, Antagonistas y Animales con el índice común.
- `personajes.sh` y el TSV del índice tenían finales de línea CRLF, que causaban el error `$'\r'`; ambos se normalizaron a LF. Después de corregir los finales de línea, la lista de Personajes abrió en Debian.
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
- **Validación:** probé la versión anterior; estas nuevas proporciones todavía estaban pendientes de revisar en Debian.
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
- La ficha de Rick se mostró con el retrato lateral y el texto legible en la terminal.
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
- En Debian abrí una ficha ampliada y una ficha breve de la selección; ambas mostraron el retrato esperado.
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
- El informe de entrega incluye las cuentas necesarias para iniciar sesión y probar el sistema.
- **Validación:** se cotejó `AGENTS.md` con las consignas recibidas. No se generó ni se validó todavía el `.ova` o el informe final.


### 2026-11-09 17:24 ART — Corrección de la continuación en THE REFUGE

- El reporte indicó que la aplicación se cerraba al continuar la partida en la confrontación final. La revisión de `src/refuge/refuge.py` localizó la causa: `final_decision()` entregaba opciones de tres valores, pero `choose()` esperaba pares de etiqueta y descripción. El desempaquetado fallaba al construir el menú.
- Se corrigió el formato de las opciones y se conservaron sus ayudas dentro de las descripciones. La lógica de desenlaces y el guardado no se modificaron.
- **Validación:** revisión estática del código en `main`; todavía no ejecutado en la VM Debian.
- **Pendiente:** sincronizar `src/refuge/refuge.py` con Debian y reanudar la partida guardada en `CONFRONTACIÓN FINAL` para elegir un desenlace y confirmar que queda guardado como finalizado.

### 2026-11-09 18:06 ART — Prueba de reflejos en THE REFUGE

- Se incorporó a la confrontación final una secuencia textual de tres señales aleatorias (W, A, S o D), con 2,5 segundos por señal y respuesta directa de tecla, sin Enter. Cada acierto añade 2 puntos al puntaje del desenlace.
- El resultado registra los aciertos de reflejos y el puntaje junto con el desenlace. El modo de terminal se restaura al terminar la secuencia.
- **Validación:** la campaña llegó a un desenlace en Debian; el QTE todavía estaba pendiente de probar.
- **Pendiente:** sincronizar la actualización en la VM Debian y comprobar aciertos, errores, tiempo agotado, puntaje final y que el terminal queda usable al salir.

### 2026-11-09 22:42 ART — Arena de esquiva de THE REFUGE

- La prueba de reflejos pasó de tres señales aisladas a una arena ASCII de tres oleadas durante 18 segundos. El jugador se mueve con WASD; aparecen Salvadores, Negan y caminantes, con obstáculos y avisos de ataque.
- La arena tiene tres vidas; Q permite terminarla. Cada ataque anunciado que se esquiva añade 2 puntos al desenlace, con un máximo de 6. La lógica restaura el modo previo de la terminal al salir.
- **Validación:** la arena todavía no se había probado en Debian. La versión anterior de la campaña ya llegaba a un desenlace.
- **Pendiente:** sincronizar la actualización en la VM Debian y comprobar movimiento, avisos, daño, puntaje, desenlace guardado y estado de la terminal al salir.

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

### 2026-11-09 23:45 ART — Ejecución directa de THE REFUGE en Debian

- THE REFUGE abrió al ejecutar directamente el módulo corregido en Debian, después de agregar los dos puntos que faltaban en `final_decision`.
- **Alcance:** se probó la ejecución directa del módulo. Todavía faltaba revisar la entrada desde el menú principal y completar una campaña.
- **Pendiente:** confirmar la apertura desde bin/alexandria y recorrer los desenlaces en Debian.

Al cerrar cada tarea, agregá una entrada cronológica a este historial sin borrar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.

### 2026-11-10 — Versión de desarrollo 0.3

- El lanzador `bin/alexandria` ahora muestra `ALEXANDRIA OS 0.3`; se centralizó el número de versión en una variable para facilitar futuros cambios.
- Se añadió la categoría **¿Qué es THE REFUGE?**. Todas las opciones de campaña y las tres decisiones finales muestran su probabilidad de éxito/fallo y las estadísticas relacionadas. Los fracasos no conceden los beneficios de la opción y conservan costes o penalizaciones.
- La arena pasó de 28 × 9 a 40 × 14, incorporó cobertura adicional, tres enemigos iniciales y cuatro refuerzos (hasta siete en total), cuatro oleadas de 22 segundos y una velocidad enemiga aproximadamente 10 % mayor.
- **Validación:** el cambio quedó registrado en GitHub `main`; la versión 0.3 aún no se ejecutaba en Debian. El arranque directo ya funcionaba en la versión anterior.
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

### 2026-11-17 — Cierre de la versión 0.6

- Preparé la imagen `Alexandria_OS_0.6.ova` sobre Debian 13 sin entorno gráfico e importé la máquina en VirtualBox.
- Recorrí las tres secciones principales desde el menú: THE WORLD, THE COMIC ARCHIVE y THE REFUGE.
- THE WORLD quedó organizado con Personajes, Animales, Caminantes, Antagonistas, Comunidades, Ubicaciones, Cronología, Observaciones, Glosario y Recorrido de Rick.
- El menú principal conserva seis opciones y la selección en rojo de la interfaz.
- En el cierre prioricé **BASE-04** (menú principal en Debian) y **PKG-02 — ZIP** (contenido del paquete y manifiesto SHA-256). La matriz manual registra 33 casos aprobados, 11 pendientes y 0 fallidos.
- El informe final en PDF acompaña la OVA e incluye el enlace directo para descargarla.

