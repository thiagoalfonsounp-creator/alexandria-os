# Primera verificación local — Alexandria OS 0.5

**Fecha:** 2026-11-10, 21:40 ART (UTC−3)  
**Actualización de auditoría:** 2026-11-11, 01:45 ART (UTC−3)  
**Aplicación local:** 2026-11-11, 02:12 ART (UTC−3)  
**Entorno:** copia local de trabajo en PowerShell.  
**Alcance:** inspección estructural, ajuste de visores y empaquetado; no se ejecutó la interfaz.

## Resultados confirmados por inspección local

- `personajes_index.tsv`: encabezado de ocho columnas correcto, 249 filas, 248 expedientes únicos, sin filas con cantidad incorrecta de columnas y sin rutas de ficha faltantes.
- Conteos por categoría: 225 `PERSONAJE`, 6 `ANTAGONISTA`, 14 `CAMINANTE`, 4 `ANIMAL`.
- No hay fichas vacías en `data/world/personajes/`.
- Los índices de Comunidades, Ubicaciones, Glosario, Cronología y Recorrido de Rick tienen, respectivamente, 13, 19, 41, 34 y 14 filas. No se encontraron IDs repetidos, filas mal formadas, archivos faltantes ni archivos vacíos.
- Los siete documentos de WALKER DATABASE y los tres de FIELD OBSERVATIONS existen y no están vacíos.
- Los 14 scripts y lanzadores Bash del proyecto quedaron sin finales de línea CRLF; se normalizaron `observaciones.sh` y `antagonistas.sh` a LF según `.gitattributes`. Es una revisión estática, no una ejecución de Bash.
- Los 46 archivos añadidos en la versión 0.4 existen en esta copia; todos tienen `ESTADO DE EVIDENCIA: CONFIRMED`, una línea `REFERENCIA PRIMARIA` y una nota `COTEJO`. Los 46 pertenecen a las primeras 60 fichas PERSONAJE. Esto confirma el estado registrado en el contenido y la nota del propietario; no constituye un cotejo independiente de cada escena.
- Quedan 527 valores `UNCONFIRMED` en 187 expedientes únicos: 170 arcos, 170 primeras apariciones y 187 últimas apariciones. La cola individual está en [cotejo_primario_pendiente_0.5.csv](cotejo_primario_pendiente_0.5.csv).

## Pendientes de ejecución y fuentes

- La matriz manual sigue pendiente para la interfaz. La VM observada muestra Alexandria OS 0.4; esta copia local corresponde a 0.5.
- El paquete anterior `alexandria-os-debian-sync-0.5.tar.gz` conserva lectores de dimensiones fijas. El paquete actual `alexandria-os-0.5-verificacion.tar.gz` contiene los lectores adaptativos, acepta un lanzador 0.4 o 0.5 y ya conserva permisos: 16 archivos ejecutables, incluidos `bin/alexandria`, `bin/instalar-comandos` y los scripts `.sh`. La inspección estructural del tar pasó; todavía no se instaló ni ejecutó en Debian.
- No se pudo ejecutar Bash ni `dialog` en Windows: WSL no está instalado y no se encontraron `bash` o `sh` disponibles. La matriz conserva 79 casos pendientes y cero aprobados; no se registró ninguna ejecución manual.
- La cola CSV conserva 527 filas con estado `Pendiente de cotejo primario`; las 527 tienen vacíos los campos de evidencia, fecha y hora.
- En `imports/comics/` solo está `.gitkeep`, y no se encontraron archivos PDF/CBZ/CBR/RAR en el espacio de trabajo. Por eso no se cotejaron escenas ni apariciones contra ejemplares primarios y ningún valor `UNCONFIRMED` cambia de estado.
- Esta auditoría no valida contenido de canon, navegación de teclado, diseño visual ni ejecución de Bash/`dialog` en Debian.

## Próximo orden de verificación

1. Instalar el paquete actual en Debian con respaldo y verificar que el lanzador quede en 0.5.
2. Ejecutar los casos de la matriz en Debian y registrar una observación por pantalla y categoría; incluir las categorías de WALKER DATABASE en 80×24 y 120×40.
3. Cotejar la cola CSV contra ejemplares primarios, guardando referencia de número y escena para cada campo cuando los cómics estén disponibles. Mantener `UNCONFIRMED` si la evidencia no lo resuelve.

