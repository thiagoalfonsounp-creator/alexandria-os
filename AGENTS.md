# Reglas del proyecto Alexandria OS

Estas reglas se aplican a Alexandria OS y a sus subdirectorios. El repositorio privado de GitHub es la fuente de verdad del proyecto: <https://github.com/thiagoalfonsounp-creator/alexandria-os>.

## Objetivo y registro

- Alexandria OS es una distribución personalizada basada en Debian 13 para consultar el universo de *The Walking Dead*, organizar una biblioteca personal y desarrollar una experiencia de supervivencia.
- Mantené `README.md` actualizado con el estado comprobado del proyecto. Al cerrar cada tarea, agregá una entrada cronológica con cambios, archivos afectados, validaciones y pendientes. No borres entradas anteriores.
- Separá el diseño propuesto, los cambios presentes en archivos y el comportamiento ejecutado y comprobado en Debian. No declares una función verificada solo por inspeccionar el código.

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
- Mantené `data/world/personajes_index.tsv` como índice del selector de personajes. Cada entrada debe apuntar a una ficha existente y distinguir fichas ampliadas, breves, animales y caminantes identificados.
- El alcance del archivo principal es la serie regular, números 1-193, y su epílogo. Identificá por separado los materiales complementarios que queden fuera de ese alcance.
- Registrá ubicaciones relevantes para la historia, la supervivencia o los conflictos.
- Ordená las cronologías según el orden interno de los acontecimientos. Marcá como aproximadas o desconocidas las fechas que el cómic no precise.
- Representá el recorrido de Rick y su grupo como un mapa esquemático, no como navegación a escala.
- Mantené una estética de archivo documental con referencias visuales al cómic, sin incorporar páginas, paneles ni otro material protegido al repositorio o a paquetes compartidos.

## Implementación y datos

- La interfaz usa Bash y `dialog`; conservá la navegación por teclado y los textos en español.
- Guardá los expedientes de texto en `data/` y conectá cada opción del menú con su archivo o módulo correspondiente.
- Conservá los permisos ejecutables de los scripts de `bin/` y `src/`.
- Algunos scripts asumen `/home/walker/alexandria-os` o `$HOME/alexandria-os`. Si se cambian esas rutas, actualizá todos los puntos afectados y documentá el nuevo requisito.
- Los cómics PDF o CBZ son archivos locales del usuario. No los agregues al repositorio ni a paquetes distribuibles.

## Validación

- Indicá qué se ejecutó, en qué entorno y qué resultado se observó.
- Conservá como pendientes las comprobaciones que no se realizaron.
- Al registrar avances, usá fecha y hora de Argentina (ART, UTC−3) cuando estén disponibles.
