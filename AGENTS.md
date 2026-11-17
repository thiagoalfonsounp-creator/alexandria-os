# Reglas del proyecto Alexandria OS

Estas reglas se aplican a Alexandria OS y a sus subdirectorios. El repositorio privado de GitHub es la fuente de verdad del proyecto: <https://github.com/thiagoalfonsounp-creator/alexandria-os>.

## Objetivo y registro

- Alexandria OS es una distribución personalizada basada en Debian 13 para consultar el universo de *The Walking Dead*, organizar una biblioteca personal y desarrollar una experiencia de supervivencia.
- El perfil objetivo es un usuario hispanohablante interesado en el cómic de *The Walking Dead* que necesita una interfaz de terminal clara para consultar y organizar su biblioteca. Documentá las necesidades reales del usuario sin inventar datos personales.
- La entrega académica final consiste en una imagen virtual `.ova` de un sistema Debian completo y usable, más un informe final exclusivamente en PDF. Mantené ambos artefactos de entrega fuera del repositorio Git; si el `.ova` supera el límite del medio de entrega, alojalo en la unidad autorizada y añadí el enlace de descarga al PDF.
- Mantené `README.md` actualizado con el estado comprobado del proyecto. Al cerrar cada tarea, agregá una entrada cronológica con cambios, archivos afectados, validaciones y pendientes. No borres entradas anteriores.
- Separá el diseño propuesto, los cambios presentes en archivos y el comportamiento ejecutado y comprobado en Debian. No declares una función verificada solo por inspeccionar el código.

## Entrega académica

- El informe PDF debe incluir: nombre, logo y versión de la distribución; descripción del perfil de usuario; nombre de usuario y contraseña para la cuenta normal y para root; aplicaciones instaladas con una descripción breve; explicación del menú principal; tecnologías utilizadas; manual de uso; comandos y alias añadidos; y una descripción completa del trabajo que permita al docente acceder al sistema y probarlo.
- Para cada archivo del sistema editado o reemplazado —por ejemplo, `.bashrc`, `/etc/issue` o la configuración de GRUB— documentá su ruta exacta, estado previo, cambio realizado, motivo, procedimiento y efecto comprobado. Incluí también las decisiones de instalación y configuración que no estén representadas por un archivo del repositorio.
- Si se instalaron aplicaciones propias o compiladas fuera de los repositorios oficiales, identificá cada aplicación y documentá su origen, versión, dependencias, pasos de instalación/compilación y configuración. No presentes paquetes supuestos como instalados.
- Usá español claro de Argentina y formato académico consistente, con referencias para las fuentes consultadas. La explicación y las capturas del menú deben corresponder a la interfaz real del sistema.
- Alexandria OS no debe incorporar un entorno gráfico: la interfaz de usuario es textual y en español. No agregues escritorio gráfico para cumplir la consigna ni presentes capturas de una interfaz gráfica como evidencia válida; usá capturas legibles del menú y las aplicaciones de terminal.
- No incluyas cómics PDF/CBZ protegidos en el `.ova`, el PDF ni otros materiales compartidos. Explicá que `imports/comics/` es para archivos personales del usuario.
- La consigna académica requiere que el PDF final informe las credenciales de las cuentas normal y root. El agente nunca debe pedir, repetir ni guardar contraseñas reales en chats, Git, README, `AGENTS.md`, capturas o registros. En borradores usá campos para completar; el propietario agregará localmente las credenciales verificadas al PDF final y lo entregará por un medio privado. No inventes credenciales ni afirmes que root tiene contraseña si no se comprobó.
- No guardes el `.ova` ni el PDF final en Git salvo que el usuario lo solicite expresamente y el repositorio esté destinado a esas entregas. Conservá los enlaces de descarga fuera del historial de Git y comprobá que el enlace del PDF corresponda al archivo realmente entregado.

## Canon y fuentes

- Usá como canon narrativo principal el cómic de *The Walking Dead*.
- No uses la serie de televisión ni los videojuegos para completar vacíos del cómic.
- Usá los nombres establecidos en el cómic. No traslades apellidos de la adaptación televisiva cuando el cómic no los establece; si el nombre varía entre medios, registrá la incertidumbre.
- Diferenciá los hechos mostrados directamente en el cómic, las observaciones de conducta y las declaraciones de Robert Kirkman. Identificá las fuentes autorales —por ejemplo, *Letter Hacks*— y sus números de edición.
- Si una fuente no establece un dato, conservá la incertidumbre. No inventes una explicación, fecha, duración ni mecanismo.
- Usá las etiquetas de evidencia exactamente como `CONFIRMED`, `OBSERVED` y `UNCONFIRMED`.
- Usá inventarios de fans para localizar nombres, no como sustituto del cómic. En una ficha sin número o escena comprobados, indicá `UNCONFIRMED` y dejá pendiente la referencia primaria.

## Registros de campo

Cada registro de `FIELD OBSERVATIONS` debe conservar estos campos y este orden:

1. `Observation ID`
2. `Subject`
3. `Comic Reference`
4. `Description`
5. `Analysis`
6. `Evidence Level`
7. `Conclusion`

Describí primero la escena y separá de ella cualquier interpretación. No presentes una conducta observada una sola vez como una regla universal.

## Organización del contenido

- Reservá expedientes completos para personajes de relevancia narrativa alta. Incluí información interesante de personajes secundarios cuando aporte al archivo.
- Mantené `data/world/personajes_index.tsv` como índice de personajes, antagonistas, animales y caminantes identificados. Sus columnas son `PERSONAJE`, `GRUPO`, `TIPO`, `NIVEL`, `ARCO`, `PRIMERA_APARICION`, `ULTIMA_APARICION` y `ARCHIVO`. Cada entrada debe apuntar a una ficha existente y distinguir esas categorías y los niveles de detalle. Si una ficha corresponde a más de una categoría, permití varias filas que apunten al mismo archivo y contá el perfil único una sola vez.
- En los selectores de Personajes y Antagonistas, mostrá el nombre limpio y, en la columna de detalle, el tomo/arco de debut más los números de primera y última aparición cuando estén confirmados. No muestres las categorías internas de nivel de detalle; `NIVEL` se conserva para el formato de las fichas y los retratos. El intervalo indica los extremos, no que el personaje aparezca en cada número intermedio. Si la fuente primaria no permite confirmarlos, usá `Arco no confirmado` y dejá los campos correspondientes como `UNCONFIRMED`; no deduzcas el arco a partir de la comunidad o la familia.
- El alcance del archivo principal es la serie regular, números 1-193, y su epílogo. Identificá por separado los materiales complementarios que queden fuera de ese alcance.
- Registrá ubicaciones relevantes para la historia, la supervivencia o los conflictos.
- Ordená las cronologías según el orden interno de los acontecimientos. Marcá como aproximadas o desconocidas las fechas que el cómic no precise.
- Representá el recorrido de Rick y su grupo como un mapa esquemático, no como navegación a escala.
- Mantené una estética de archivo documental con referencias visuales al cómic, sin incorporar páginas, paneles ni otro material protegido al repositorio o a paquetes compartidos.

## Implementación y datos

- La interfaz conserva Bash y `dialog` en sus módulos. El menú principal usa Python/curses y Chafa para representar el logo en la terminal; mantené la navegación por teclado, los textos en español y el funcionamiento sin escritorio gráfico.
- Guardá los expedientes de texto en `data/` y conectá cada opción del menú con su archivo o módulo correspondiente.
- Conservá los permisos ejecutables de los scripts de `bin/` y `src/`.
- Algunos scripts asumen `/home/walker/alexandria-os` o `$HOME/alexandria-os`. Si se cambian esas rutas, actualizá todos los puntos afectados y documentá el nuevo requisito.
- Los cómics PDF o CBZ son archivos locales del usuario. No los agregues al repositorio ni a paquetes distribuibles.
- Mantené la instalación sin entorno gráfico y asegurá que el menú, los mensajes, el manual y la experiencia de primer inicio usen español de Argentina.
- Al documentar comandos o alias, registrá su nombre, propósito, archivo donde se definieron y modo de uso; no afirmes que existen hasta revisar la configuración del sistema.

## Validación

- Indicá qué se ejecutó, en qué entorno y qué resultado se observó.
- Antes de entregar el `.ova`, exportá la VM completa e importala en VirtualBox como comprobación independiente. Verificá que arranque, que la cuenta normal permita entrar, que root funcione según la configuración real, que el menú principal y las categorías previstas se puedan recorrer y que las aplicaciones declaradas estén disponibles. No incluyas contraseñas en la bitácora de estas pruebas.
- Antes de entregar el PDF, cotejá cada afirmación con la VM, el repositorio o una fuente citada. Revisá que enumere archivos de sistema cambiados, aplicaciones, tecnologías, manual, comandos/alias y las instrucciones de acceso y prueba; que las capturas sean del entorno textual; y que el enlace al `.ova` abra el artefacto correcto cuando corresponda.
- La presencia del archivo `.ova`, del PDF o de una captura no demuestra que el sistema arranque ni que la función opere; registrá los resultados reales de la importación y la prueba.
- Conservá como pendientes las comprobaciones que no se realizaron.
- Al registrar avances, usá fecha y hora de Argentina (ART, UTC−3) cuando estén disponibles.
