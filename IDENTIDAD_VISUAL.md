# Alexandria OS — Identidad visual

**Estado:** primera aplicación en GitHub main: paleta monocromática compartida desde el lanzador, franja de archivo en el menú principal y rayas diagonales en los marcos de retrato. El cambio aún no se ejecutó ni se comprobó en Debian.

## Dirección

Alexandria OS conserva una interfaz exclusivamente textual y navegable con teclado. Su identidad toma el blanco y negro entintado del cómic, con grises y tramas de rayas diagonales, dentro de la estructura ordenada y sobria de un expediente documental.

La estética del cómic debe aparecer en el marco, los márgenes, los encabezados y el tratamiento de los retratos. La información de las fichas debe seguir pareciendo un registro serio: clara, jerárquica y fácil de consultar. La textura nunca debe competir con la lectura.

## Decisiones confirmadas

- Mantener la organización de archivo documental y el vocabulario de expediente.
- Reemplazar el azul intenso de la interfaz actual por una paleta estrictamente monocromática: negro, blanco y grises neutros.
- Evocar la tinta impresa mediante rayas diagonales y medias tintas, aplicadas con moderación a márgenes, marcos y retratos.
- Mantener las fichas sobrias: títulos de sección claros, identificadores y estados de evidencia visibles, párrafos legibles y sin adornos que distraigan.
- Conservar una identidad común para **THE WORLD**, **THE COMIC ARCHIVE** y **THE REFUGE**.
- Mantener toda la experiencia en la terminal. No se planifica una interfaz gráfica.
- Usar la fuente monoespaciada disponible en la terminal. La jerarquía se construye con mayúsculas, espaciado, marcos y selección inversa; no se reemplaza la fuente del sistema.
- Mantener navegación por teclado y evitar el desplazamiento horizontal.

## Sistema visual

| Uso | Tratamiento |
| --- | --- |
| Fondo general | Negro o gris muy oscuro, sin azul saturado ni acentos de color. |
| Superficie de ficha | Gris claro o blanco papel, con texto negro de alto contraste. |
| Marcos | Líneas simples y regulares; el peso visual viene de la tinta y de pequeñas zonas tramadas. |
| Texto principal | Negro sobre superficie clara, monoespaciado y sin textura de fondo. |
| Encabezados | Mayúsculas y espaciado claro; conservar el nombre del módulo y el identificador del expediente. |
| Selección | Video inverso en blanco y negro y un marcador de cursor; no depender de un color para indicar foco. |
| Estados | Etiquetas explícitas como CONFIRMED, OBSERVED y UNCONFIRMED, además de símbolos cuando ayuden. |
| Trama | Rayas diagonales o medias tintas solo en márgenes, separadores, marcos y retratos. |
| Retrato | Representación monocromática de alto contraste, en un panel lateral proporcionado a la ficha. |

Las tramas no deben quedar detrás del texto ni reducir el contraste. La selección y los estados deben seguir distinguiéndose en terminales que solo muestren 16 colores o trabajen en monocromo.

## Criterios para las fichas

- Conservar los campos de expediente: identificador, nombre, fuente, alcance, estado de evidencia y secciones narrativas.
- Mantener el cuerpo del texto alineado a la izquierda, con párrafos recompuestos y ajustados al ancho disponible.
- Reservar un panel lateral contenido para los retratos seleccionados; el espacio no debe ensancharse más de lo necesario ni estrechar demasiado la columna de lectura.
- Mostrar los retratos en caracteres monocromos mediante chafa. Si falta una imagen o la herramienta, la ficha debe seguir completa y legible sin retrato.
- No usar globos de diálogo, onomatopeyas ni composiciones recargadas dentro del expediente.
- Mantener el avance vertical del texto y los controles de desplazamiento visibles.

## Reglas de pantalla

- Mantener una cabecera con módulo, nombre de la sección e identificador del registro.
- Usar una superficie clara para fichas extensas y un fondo oscuro fuera del panel.
- Reservar las rayas para espacios no informativos: bordes, separadores, márgenes o una franja alrededor del retrato.
- Ajustar el contenido al terminal y no cortar palabras de forma que cambie su sentido.
- Mantener una leyenda breve de teclas al pie: mover, abrir, volver y salir.
- Dar la misma jerarquía a los estados de evidencia en todas las categorías.
- Reutilizar el lenguaje visual en menús, índices y expedientes sin convertirlos en pantallas gráficas.

## Boceto de dirección para el menú

~~~text
+------------------------------------------------------------------------------+
| ALEXANDRIA OS // ARCHIVO DE SUPERVIVIENTES                                   |
| /////////------------------------------------------------------------------- |
| > 01  THE WORLD                         REGISTRO DEL SISTEMA                  |
|   02  THE COMIC ARCHIVE                 ARCHIVO LOCAL: DISPONIBLE             |
|   03  THE REFUGE                                                             |
|------------------------------------------------------------------------------|
| [↑/↓] MOVER   [ENTER] ABRIR   [ESC] VOLVER   [Q] SALIR                       |
+------------------------------------------------------------------------------+
~~~

Las rayas representan una trama de borde, no un fondo para texto. El esquema expresa una jerarquía textual; no implica una interfaz gráfica.

## Boceto de ficha

~~~text
+-------------------- THE WORLD / PERSONAJES · TW-PER-001 --------------------+
| EXPEDIENTE: RICK GRIMES              FUENTE: THE WALKING DEAD · CÓMIC       |
|-----------------------------------------------------------------------------|
| IDENTIFICACIÓN                                      +---------------------+ |
| Richard Grimes. Ayudante del sheriff local.        | ////// RETRATO ///// | |
|                                                     | //// MONOCROMO ///// | |
| RECORRIDO                                           +---------------------+ |
| Despierta en un hospital cuando la sociedad ya colapsó. Busca a su familia. |
|                                                                             |
| EVIDENCIA: CONFIRMED                                                        |
| [↑/↓] DESPLAZAR                                      FICHA 20%              |
+------------------------------------------------------------------------------+
~~~

El retrato queda subordinado al expediente y la trama se mantiene dentro de su marco. El texto de ejemplo solo ilustra la composición.

## Estado y próximos pasos

La primera aplicación de la propuesta ya está en el repositorio: config/dialogrc define la paleta, bin/alexandria la carga desde el lanzador y el visor de personajes añade rayas al marco de los retratos. El visor ya representa retratos seleccionados mediante chafa. La nueva presentación todavía no se ha ejecutado ni comprobado en la VM Debian.

El siguiente paso es copiar la actualización a Debian y revisar el menú principal y una ficha representativa con retrato, comprobando contraste, lectura y navegación. No se considera validada una pantalla hasta verla ejecutada en Debian.
