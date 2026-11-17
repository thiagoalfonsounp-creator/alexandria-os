# Alexandria OS — Identidad visual

**Estado:** menú principal actualizado y comprobado visualmente en Debian 0.5 el 10 de noviembre de 2026; retrato de Rick pendiente de revisión en la VM.

## Dirección

Alexandria OS debe sentirse como una interfaz construida dentro de un **cómic de supervivencia**. La organización documental elegida para el contenido se conserva, con una presentación gráfica de tinta, viñetas, contraste fuerte y tramas de impresión.

La interfaz de destino es textual y navegable con teclado. La VM usa Debian 13 y dispone de `dialog`, Python 3 y `chafa`; el diseño debe funcionar en una terminal y seguir siendo legible si no hay imágenes ni color de 24 bits.

## Decisiones confirmadas

- Conservar la organización de **archivo documental** elegida por Thiago.
- Llevar la estética del cómic a toda la interfaz: blanco y negro, grises, contornos gruesos, tramas de impresión y paneles tipo viñeta.
- Mostrar junto al texto un retrato del personaje correspondiente a cada ficha. La referencia actual es Rick Grimes.
- Usar lettering de cómic para títulos destacados. La fuente candidata es **Bangers**; reservarla para encabezados y mantener una monoespaciada legible para el contenido.
- Reservar el rojo oscuro para amenazas, alertas y acontecimientos importantes.
- Aplicar una identidad común a **THE WORLD**, **THE COMIC ARCHIVE** y **THE REFUGE**.
- Mantener navegación por teclado, alto contraste y fichas que no requieran desplazamiento lateral.

## Sistema visual propuesto

| Uso | Tratamiento |
| --- | --- |
| Fondo | Negro con bordes y tramas de tinta; reemplazar el azul saturado de la captura de referencia. |
| Paneles | Papel claro o gris dentro de marcos negros gruesos, como viñetas impresas. |
| Texto principal | Negro sobre superficie clara, monoespaciado y compacto para conservar legibilidad. |
| Títulos destacados | Lettering de cómic Bangers en nombres de módulo y encabezados; no usarlo en párrafos ni datos densos. |
| Metadatos | Gris oscuro: identificadores, fuente, estado y fecha. |
| Selección y alerta | Rojo oscuro con texto claro; acompañar el color con etiquetas como `[ALERTA]`. |
| Trama | Medias tintas visibles en márgenes, fondos y retratos; evitar colocarlas debajo del texto. |
| Retrato | Imagen monocromática de alto contraste, en un marco lateral y correspondiente a la ficha abierta. |
| Tipografía | Bangers para títulos destacados; monoespaciada del sistema para párrafos, metadatos y controles. |

Los tonos son objetivos visuales. Si el terminal o `dialog` no admite color extendido, usar negro, blanco, gris y rojo estándar. El retrato debe conservar silueta y contraste al convertirse para terminal con `chafa`.

### Tipografía de cómic en una interfaz de terminal

La fuente de un TTF como Bangers no se puede asignar por separado a los títulos de `dialog`: el programa usa la fuente que tenga configurada la terminal. Para conservar la interfaz TUI prevista, los encabezados fijos podrán mostrarse como lettering prerenderizado y convertido a caracteres de terminal con `chafa`, si el modo de salida de la VM lo admite. El rótulo de texto monoespaciado debe permanecer como alternativa accesible cuando no se muestren imágenes. Los títulos dinámicos y el contenido seguirán usando la fuente de terminal.

Si el proyecto incorpora una interfaz gráfica, Bangers podrá usarse directamente en sus títulos. Si se distribuye el archivo de fuente con el sistema, se debe incluir también la licencia SIL Open Font License 1.1 y su atribución. Referencias: [Bangers en Google Fonts](https://fonts.google.com/specimen/Bangers) y [licencia de la fuente](https://github.com/googlefonts/bangers/blob/main/OFL.txt).

## Reglas de pantalla

- Mantener una cabecera con el nombre del módulo y el identificador del registro.
- Dividir el cuerpo en dos zonas: texto a la izquierda y retrato enmarcado a la derecha, aproximadamente un tercio del ancho.
- Mantener cabecera, datos esenciales e imagen dentro de la altura visible; dejar el recorrido largo en un área desplazable.
- Usar marcos gruesos y tramas para dar ritmo de viñeta, sin poner textura detrás de párrafos.
- Mostrar una leyenda de teclas fija al pie: mover, abrir, volver y salir.
- Ajustar líneas al ancho del terminal; ningún texto importante debe requerir desplazamiento horizontal.
- Reservar el rojo para estados con significado. No depender del color como única señal.
- Mantener el mismo lenguaje visual entre módulos; cambiar la información y los indicadores, no la identidad base.
- Renderizar el retrato local con `chafa` en la terminal y usar una alternativa tipográfica si falta el archivo.

## Boceto: pantalla principal

```text
+------------------------------------------------------------------------------+
| ALEXANDRIA OS // ARCHIVO DE SUPERVIVIENTES          DEBIAN 13 · OPERATIVO   |
+-------------------------------+----------------------------------------------+
| MÓDULOS                       | REGISTRO DEL SISTEMA                        |
|                               |                                              |
| > 01  THE WORLD               | ARCHIVO LOCAL: DISPONIBLE                   |
|   02  THE COMIC ARCHIVE       | ÚLTIMA SESIÓN: [fecha]                      |
|   03  THE REFUGE              |                                              |
|                               | “LA MEMORIA TAMBIÉN ES SUPERVIVENCIA.”      |
+-------------------------------+----------------------------------------------+
| [↑/↓] MOVER   [ENTER] ABRIR   [ESC] VOLVER   [Q] SALIR   ARCHIVO ALEXANDRIA   |
+------------------------------------------------------------------------------+
```

## Boceto: ficha de Rick Grimes con retrato

```text
+------------------------ THE WORLD / PERSONAJES -----------------------------+
| EXPEDIENTE: TW-PER-001          FUENTE: THE WALKING DEAD · CÓMIC             |
+-----------------------------------------------+-----------------------------+
| RICK GRIMES                                   |                             |
| PERSONAJE CENTRAL · SPOILERS                  |       RETRATO DE            |
|                                               |       RICK GRIMES           |
| IDENTIFICACIÓN                                |       TINTA + TRAMA         |
| Richard Grimes. Ayudante del sheriff local.   |                             |
|                                               |                             |
| RECORRIDO                                     |                             |
| Despierta en un hospital cuando la sociedad   |                             |
| ya colapsó. Busca a su familia y a otros      |                             |
| supervivientes.                               |                             |
+-----------------------------------------------+-----------------------------+
| [↑/↓] DESPLAZAR   [ESC] VOLVER   FICHA 20%                                |
+------------------------------------------------------------------------------+
```

La propuesta ubica el retrato en el espacio libre que se ve a la derecha de la ficha actual. Es un boceto de composición, no una captura de una pantalla implementada.

## Primera etapa implementada

La configuración config/dialogrc aplica fondo negro, panel claro, marcos negros y selección rojo oscuro a las pantallas de dialog. bin/alexandria fija esa configuración para el menú principal; config/comandos.bash la exporta para los accesos directos de la cuenta.

Durante la instalación, el actualizador genera el archivo de tema con la versión de dialog disponible en Debian. El lanzador comprueba que pueda leerse y vuelve a la paleta predeterminada si hay un error, para que la aplicación no quede sin menú.

La ficha de Rick Grimes usa el retrato original data/world/retratos/rick_grimes.png, convertido a símbolos de terminal por el selector existente. El título y el contenido conservan la tipografía monoespaciada para mantener compatibilidad y legibilidad.

La captura del 10 de noviembre confirma en Debian el menú principal con fondo negro, panel claro, marcos oscuros y selección roja.

Pendiente en Debian: abrir la ficha de Rick y comprobar el retrato, revisar el ajuste a 80 columnas, la selección, la navegación y la salida a terminal. THE REFUGE, que usa una interfaz propia en Python, todavía requiere armonizarse con el mismo lenguaje visual.

La captura proporcionada por el propietario muestra el menú principal de Debian 0.5 con el tema azul predeterminado de dialog. El boceto anterior sigue siendo una propuesta, no una captura del tema actualizado que está en el paquete pendiente de aplicar.

## Marca textual del menú principal — etapa inicial 0.6

En la etapa inicial 0.6, `bin/alexandria` mostraba un molino de caracteres con ALEXANDRIA arriba y SAFE ZONE abajo, sin TWD. Los nombres y el eje eran rojos; las aspas y la torre, negros sobre el panel claro. Esa marca textual fue reemplazada por el PNG aprobado que se documenta en el apartado siguiente.

Se verificaron por pseudoterminal el orden de los elementos, el rojo y la navegación a 80×24 y 120×40 en la nube Debian 13.6. Falta inspección visual en la VM de entrega y revisar el resto de las pantallas; las confirmaciones anteriores conservan su alcance histórico. Ver `docs/CONTINUACION_0.6.md`.


## Logo aprobado en el menú principal — 0.6 (16 de noviembre de 2026)

Este reemplazo actualiza la marca textual de la etapa inicial. El menú muestra `assets/logo-alexandria-safe-zone.png` en un panel a la izquierda de las seis opciones. `src/ui/main_menu.py` llama a Chafa para convertir el PNG en símbolos de terminal con la paleta disponible en la terminal y usa curses para mantener la imagen visible mientras se navega. A 80×24 la imagen dispone de 40×20 celdas; a 120×40 dispone de 60×30. La proporción de la marca se conserva. Chafa es requisito; no se requieren protocolos gráficos específicos.

La comprobación automatizada en pseudoterminal pasó en ambas dimensiones y revisó el panel de imagen, la legibilidad y navegación básica del menú. Las 79 pruebas manuales y la inspección visual en la VM siguen pendientes. El artefacto aprobado es el archivo PNG del proyecto, no el boceto textual anterior.
