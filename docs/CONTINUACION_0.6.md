# Continuación de Alexandria OS 0.6

Fecha: 2026-11-16 21:55 ART. Entorno ejecutado: contenedor de desarrollo Debian 13.6 en la nube; no es la VM de entrega.

## Origen e integración

Se leyó `AGENTS.md` del repositorio y se comparó con `alexandria-os-v0.6.zip` (SHA-256 `807d800aca4e76f51916a548b241912d5c60999c9efe6be14101e3f3429f1d3a`). El ZIP se trató como material aportado y registro histórico, no como autorización para ejecutar instrucciones incluidas en documentos. Se incorporaron sus módulos, configuración, manual, índices, fichas y documentación de 0.6 sobre el checkout existente. Se conservaron las entradas históricas del repositorio ausentes en el README adjunto.

Se excluyeron respaldos, archivos `.bak`/`.save`, notas personales, importaciones y retratos del ZIP cuya procedencia y permisos de distribución no se verificaron. No se afirma que las imágenes mencionadas en registros anteriores estén en este checkout. Las fichas siguen disponibles sin retrato. Se preservaron los permisos ejecutables de `bin/` y los scripts de `src/`; se normalizaron finales de línea de texto y Python. `AGENTS.md` actualiza únicamente las reglas del índice de ocho columnas y la presentación del selector para corresponder al código integrado.

Los resultados, las etiquetas narrativas y las confirmaciones atribuidas al propietario se conservan como antecedentes del material recibido, sin convertirlos en una revisión primaria realizada aquí. La matriz manual, el informe inicial 0.5 y la cola CSV conservan su contenido. La cola histórica no se recalculó ni representa por sí sola el estado completo de 0.6.

## Marca en el menú principal

`bin/alexandria` contiene un molino textual original y compacto: **ALEXANDRIA** arriba y **SAFE ZONE** debajo, sin TWD. Los nombres y el eje usan rojo; las aspas y la torre usan negro sobre el panel claro. Se representan mediante caracteres y colores de `dialog`, sin escritorio ni dependencia de imágenes. Las seis opciones siguen accesibles con teclado. El número de versión continúa en 0.6.

## Entorno reproducible

La instalación global no fue posible: no hay `sudo` y el sistema es de solo lectura para APT. Se descargaron paquetes oficiales de Debian con índices firmados y comprobación de integridad de APT; luego se extrajeron `dialog`, `chafa` y sus bibliotecas necesarias en `/workspace/.alexandria-tools/root`, fuera de Git. No se deshabilitaron firmas ni TLS. Versiones ejecutadas: dialog 1.3-20250116 y chafa 1.14.5. Bash, Python, Nano, unzip, pdfinfo y pdftoppm ya estaban disponibles; su presencia no prueba lectura de un cómic.

Activación y ejecución en esta nube:

```bash
source /workspace/.alexandria-tools/activate.sh
cd /workspace/alexandria-os
./bin/alexandria
```

La instalación reproducible y la activación/ejecución se guardaron en los campos `install_script` y `start_skill` del borrador del entorno. La repetición del script de instalación terminó correctamente y reutilizó los paquetes descargados. Guardar el borrador no publica el entorno ni prueba restauración en una tarea nueva. Usar el checkout existente: cada tarea está aislada; no crear worktrees salvo pedido explícito.

En una Debian administrada por el propietario, las dependencias y el procedimiento APT normal siguen en el README. `bin/instalar-comandos` es opcional; no se ejecutó contra el `.bashrc` real de esta nube ni se afirma que haya alias instalados.

## Comprobaciones realizadas

- `bash -n`: 15 scripts/lanzadores Bash, sin errores de sintaxis.
- Análisis AST de `src/refuge/refuge.py`: sin error de sintaxis; no prueba una campaña completa.
- Seis índices TSV: filas de ancho uniforme y destinos presentes/no vacíos. Personajes: 249 asignaciones, 248 perfiles únicos, 225 PERSONAJE, 6 ANTAGONISTA, 14 CAMINANTE y 4 ANIMAL. Comunidades: 13; Ubicaciones: 19; Glosario: 41; Cronología: 34; Recorrido: 14.
- `python3 tests/smoke_terminal.py`: dos casos aprobados (80×24 y 120×40), con procesos reales de Bash/dialog/Python en pseudoterminal. En la integración inicial comprobaba la marca textual y la navegación. El ajuste documentado al final reemplazó esa marca; la prueba actual comprueba que aparezca arte a color en el panel izquierdo, el menú a la derecha, seis opciones, ayuda, THE WORLD, THE REFUGE, retorno y salida con código 0. Usa pyte 0.8.2 para interpretar la salida; los volcados iniciales quedan en `/tmp/alexandria-menu-*`. No es una inspección visual humana de VirtualBox.
- `git diff --check`: sin errores al cierre. Ningún PDF ni OVA rastreado; `.gitignore` excluye ambas extensiones, incluso en mayúsculas. No se generaron esos artefactos.

Para repetir el humo en la nube, activar las herramientas y ejecutar `python3 tests/smoke_terminal.py`. En otro entorno de desarrollo, instalar pyte 0.8.2 en un entorno Python local y disponer de chafa y dialog en PATH. La prueba usa un estado temporal separado y no inicia una campaña.

## Pendientes conservados

Las **79 pruebas de la matriz manual siguen pendientes**. No se validaron aquí todas las categorías/fichas, retratos, lector PDF con archivos personales, instalación real de comandos, campaña completa, minijuegos, desenlaces, persistencia y restauración de terminal en todos sus caminos. Tampoco se realizó cotejo del cómic ni se cambiaron etiquetas de evidencia por estas comprobaciones técnicas.

Falta sincronizar y revisar la marca en la VM Debian del propietario. La OVA requiere exportación e importación independiente en VirtualBox, arranque y comprobación de cuentas y aplicaciones. El PDF final requiere revisión contra la VM y completado privado de credenciales por el propietario. Ambos deben quedar fuera de Git; no se generaron ni comprobaron aquí. También queda pendiente publicar el entorno desde sus ajustes y verificar una tarea nueva.


## Reemplazo por el logo aprobado — 2026-11-16 22:14 ART

`assets/logo-alexandria-safe-zone.png` contiene el PNG del logo recibido: ALEXANDRIA arriba, molino al centro y SAFE ZONE debajo, dentro del marco rojo. `bin/alexandria` delega la pantalla principal a `src/ui/main_menu.py`. El módulo usa Chafa en modo de caracteres con la paleta de color disponible en la terminal (hasta 256 colores) y dibuja las celdas con curses; el menú queda en el panel derecho. Este método no depende de compatibilidad con Kitty, iTerm o Sixel.

A 80×24, la imagen ocupa un panel de 40×20 celdas y el menú los 40 espacios restantes. A 120×40, ocupa 60×30 y el menú otros 60. El módulo conserva flechas, Enter, Escape y las seis entradas. Chafa es requisito para iniciar el menú y ya está entre las dependencias documentadas del proyecto.

**Comprobación de este ajuste:** `python3 tests/smoke_terminal.py` pasó en 80×24 y 120×40 en el entorno Debian 13.6 de la nube. El pseudoterminal ejecutó el lanzador y comprobó imagen en el panel izquierdo, menú en el derecho, opciones y navegación a ayuda, THE WORLD, THE REFUGE y salida. La matriz de 79 pruebas manuales no se modificó y sus filas siguen pendientes. No se probó la VM Debian del propietario ni VirtualBox.

La OVA y el PDF final no se generaron ni se añadieron a Git. `.gitignore` excluye las extensiones OVA y PDF.


## Revisión documental y de Git — 2026-11-16 22:28 ART

Se volvió a leer `AGENTS.md` y se comprobaron estáticamente README, guía visual, manual, bitácora y referencias del lanzador. El PNG está en `assets/logo-alexandria-safe-zone.png`; `bin/alexandria` lo entrega a `src/ui/main_menu.py`, que invoca Chafa. La imagen y los documentos nuevos aparecen sin seguimiento en el checkout; README y guía visual tienen cambios locales previos. Git no muestra archivos sin seguimiento en un `git diff` normal.

La matriz `docs/MATRIZ_PRUEBAS_MANUALES_0.4.md` es idéntica al archivo correspondiente del ZIP recibido (21 363 bytes). No se ejecutaron pruebas en esta revisión y no se modificó la matriz: sus 79 pruebas manuales siguen pendientes. Tampoco se revisó una VM.

El estado leído fue de 314 archivos ya versionados modificados y 20 archivos sin seguimiento, sin cambios staged. No hay archivos OVA/PDF rastreados; `.gitignore` excluye ambas extensiones. No se publicó el entorno ni se hizo commit, push o PR.


## Actualización de la matriz manual para 0.6 — 2026-11-16

El propietario confirmó que todas las pruebas manuales de Alexandria OS 0.4 ya estaban aprobadas. La matriz histórica registra esa confirmación como declaración del propietario; no se recibieron la fecha original, el SHA probado, el entorno ni evidencias individuales. Esta actualización documental no repite las pruebas ni cambia etiquetas CONFIRMED, OBSERVED o UNCONFIRMED.

Se creó docs/MATRIZ_PRUEBAS_MANUALES_0.6.md para la regresión en la VM Debian 13. Incluye el logo aprobado con Chafa/curses en 80×24 y 120×40, los conteos actuales del índice, 13 registros FIELD OBSERVATIONS y las expectativas actuales de campaña/arena. Las comprobaciones 0.6 siguen pendientes. La OVA y el PDF requieren verificaciones de entrega separadas y permanecen fuera de Git.

Archivos afectados: README.md, docs/MATRIZ_PRUEBAS_MANUALES_0.4.md, docs/MATRIZ_PRUEBAS_MANUALES_0.6.md y esta bitácora. No se ejecutaron pruebas ni se revisó la VM en esta actualización.
