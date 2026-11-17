# Matriz de pruebas manuales — Alexandria OS 0.6

Actualizada el 2026-11-16 para la revisión 0.6 de la rama codex/alexandria-os-v0.6 y el PR #1. Ejecutar contra el commit exacto sincronizado en la VM Debian 13 del propietario; anotar el SHA real en cada registro. Esta matriz no declara aprobada la VM.

## Antecedente de la versión 0.4

El propietario confirmó el 2026-11-16 que todas las pruebas manuales de 0.4 ya estaban aprobadas. La matriz histórica [MATRIZ_PRUEBAS_MANUALES_0.4.md](MATRIZ_PRUEBAS_MANUALES_0.4.md) registra esa confirmación global en sus casos e identifica como no informados la fecha original, el commit probado, el entorno y las evidencias individuales. No se volvió a ejecutar 0.4 en esta actualización. La aprobación de 0.4 no se transfiere automáticamente a 0.6, especialmente donde cambiaron el menú, el logo, los datos o las funciones.

Los niveles narrativos CONFIRMED, OBSERVED y UNCONFIRMED permanecen independientes del resultado de las pruebas. Aprobar que una ficha abra no demuestra la exactitud de su canon ni cambia esas etiquetas.

## Base y expectativas 0.6

La versión objetivo integra el PNG aprobado con ALEXANDRIA sobre el molino y SAFE ZONE debajo, sin TWD. El menú principal lo representa con Chafa y curses y mantiene seis opciones. La bitácora informa una distribución de 40×20 celdas de imagen y menú a la derecha en 80×24, y 60×30 celdas de imagen y menú a la derecha en 120×40.

Los conteos registrados para la base 0.6 son: índice de personajes con 249 asignaciones y 248 perfiles únicos —225 personajes, 6 antagonistas, 14 caminantes identificados y 4 animales—; 13 comunidades; 19 ubicaciones; 41 entradas de glosario; 34 etapas de cronología; 14 documentos del recorrido de Rick. El proyecto incluye 7 documentos de WALKER DATABASE y 13 FIELD OBSERVATIONS (FO-001 a FO-013).

## Instrucciones de ejecución y registro

- Preparar snapshot de VM y copias de las partidas/cuaderno antes de pruebas que escriben datos. Usar archivos propios o autorizados; no capturar contraseñas ni páginas del cómic.
- Para cada caso y subcaso, completar responsable, SHA real, Debian/VM, terminal, dimensión, fecha y hora ART, resultado observado y evidencia. No usar una muestra para aprobar toda una lista.
- Estados de 0.6 permitidos: Pendiente, Aprobada, Fallida o Bloqueada. Cambiar un estado solo tras ejecutar y observar esa comprobación en 0.6. Registrar evidencia y reintentos sin borrar el historial.
- La columna Antecedente 0.4 resume la confirmación del propietario; no es un resultado de 0.6 ni una validación independiente de esta revisión.
- Si un paso depende de un recurso no disponible, registrar Bloqueada con la causa. Mantener separados el estado funcional y el nivel de evidencia narrativa.
- La versión cloud no sustituye la VM de entrega. No marcar la OVA ni el PDF aprobados por haber revisado archivos del repositorio.

## Casos de regresión y novedades 0.6

| ID 0.6 | Módulo | Pasos y resultado esperado en 0.6 | Casos 0.4 relacionados | Antecedente 0.4 | Estado 0.6 |
| --- | --- | --- | --- | --- | --- |
| ENV-06-01 | Entorno y versión | Sincronizar el commit del PR en Debian 13. Registrar SHA con git rev-parse HEAD, cuenta normal, ruta del checkout, stty size y disponibilidad de bash, dialog, nano, python3, pdfinfo, pdftoppm y chafa. Confirmar que se prueba la revisión exacta del PR. | BASE-01 | Aprobada según propietario | Pendiente |
| MENU-06-01 | Logo y composición | Ejecutar ./bin/alexandria. Verificar el PNG aprobado: ALEXANDRIA sobre el molino, SAFE ZONE debajo, rojo y negro, sin TWD; el logo queda a la izquierda y las seis opciones a la derecha. Revisar legibilidad y proporción en 80×24 y 120×40. | BASE-02, BASE-03 | Aprobadas según propietario; logo y layout actuales son nuevos | Pendiente |
| MENU-06-02 | Teclado, rutas y salida | Recorrer las seis opciones con flechas y Enter; probar Escape, ayuda, THE WORLD, THE REFUGE, retorno al menú y salida a la consola. Repetir desde una sesión nueva. | BASE-02, W-01, AY-01 | Aprobadas según propietario | Pendiente |
| WORLD-06-01 | Categorías | Desde THE WORLD abrir las diez categorías y volver usando Escape o Volver donde exista. Confirmar que cada opción abre el módulo que indica su nombre. | W-01 | Aprobada según propietario | Pendiente |
| DATA-06-01 | Índice y Personajes | Recorrer el selector de principio a fin. Comprobar 225 entradas PERSONAJE, 249 asignaciones y 248 perfiles únicos; revisar navegación, nombre limpio y detalle de arco/extremos cuando estén confirmados. Comprobar que Pamela figure en las dos categorías con una ficha compartida. | P-01, P-02, P-04 | Aprobadas según propietario | Pendiente |
| DATA-06-02 | 46 fichas individuales | Repetir una por una las filas F01–F46 del anexo histórico desde el selector de Personajes; leer cada ficha completa y comprobar el destino correcto. Registrar una subfila por ficha. No cambiar etiquetas narrativas por la sola apertura. | P-03, F01–F46 | Aprobadas según propietario | Pendiente |
| DATA-06-03 | Retratos y ausencia de imagen | Abrir una ficha con la imagen que esté efectivamente presente y otra sin imagen. Verificar que texto y navegación sigan disponibles y que el fallback sea claro si falta el recurso o Chafa. Registrar los recursos disponibles; no exigir retratos excluidos del checkout. | P-05 | Aprobada según propietario | Pendiente |
| DATA-06-04 | Antagonistas, animales y caminantes | Abrir todas las entradas: 6 antagonistas, 4 animales y 14 caminantes identificados. Contrastar tipos y fichas con el índice; Pamela aparece también en Personajes con ruta compartida. | A-01, AN-01, CA-01 | Aprobadas según propietario; comprobar conteo actualizado de antagonistas | Pendiente |
| WALK-06-01 | WALKER DATABASE | Abrir los 7 documentos: Perfil; Anatomía y daño; Infección y reanimación; Movilidad y sentidos; Conducta y clasificaciones; Debilidades y casos especiales; Referencias y pendientes. Leerlos en 80×24 y 120×40 y volver con Escape. | CA-02 | Aprobada según propietario | Pendiente |
| WORLD-06-02 | Comunidades, ubicaciones, glosario y cronología | Recorrer todas las entradas e intentar abrir cada destino. Esperados: 13 comunidades, 19 ubicaciones, 41 entradas de glosario y 34 etapas de cronología; conservar orden interno e incertidumbre de fechas. | CO-01, UB-01, GL-01, CR-01, CR-02 | Aprobadas según propietario; conteos de glosario/cronología actualizados | Pendiente |
| OBS-06-01 | FIELD OBSERVATIONS | Abrir FO-001 a FO-013, leer cada registro y revisar el orden de sus siete campos. Repetir los lectores en 80×24 y 120×40. Separar descripción de análisis y conservar OBSERVED cuando corresponda. | FO-01 | FO-001 a FO-003 aprobadas según propietario; FO-004 a FO-013 son nuevas en la integración | Pendiente |
| RICK-06-01 | Recorrido de Rick | Abrir los 14 documentos: tres mapas, guía de método y etapas R01–R10. Verificar retorno, lectura completa y ausencia de distancias/coordenadas inventadas. | RR-01 | Aprobada según propietario | Pendiente |
| COMIC-06-01 | Catálogo e importación | En una biblioteca de ensayo vacía comprobar el mensaje de catálogo vacío; agregar un PDF propio de dos páginas y un CBZ autorizado con espacios en el nombre y volver a abrir el catálogo. No incluir cómics protegidos. | BI-01 | Aprobada según propietario | Pendiente |
| COMIC-06-02 | Lector PDF | Abrir el PDF de ensayo; probar p/n en primera y última página, salida con q y cancelación del selector. Confirmar contador, lectura, retorno y que el terminal conserve control. Si falta un renderizador compatible, registrar bloqueo, no aprobación. | BI-02 | Aprobada según propietario | Pendiente |
| COMIC-06-03 | Errores PDF | En la copia de ensayo probar carpeta vacía y archivo PDF inválido. Confirmar mensajes comprensibles, retorno controlado y consola utilizable. | BI-03 | Aprobada según propietario | Pendiente |
| NOTE-06-01 | Cuaderno de campo | Respaldar la nota, añadir una entrada de ensayo, guardar y salir de Nano, reabrir y confirmar persistencia; restaurar el respaldo del propietario. | CU-01 | Aprobada según propietario | Pendiente |
| HELP-06-01 | Manual / ayuda | Abrir la ayuda desde la opción actual del menú y recorrer navegación, módulos, PDF y comandos. Confirmar que el texto corresponda a 0.6 y que Escape vuelva al menú. | AY-01 | Aprobada según propietario | Pendiente |
| REFUGE-06-01 | Acceso a THE REFUGE | Abrir THE REFUGE desde el menú, consultar su introducción y salir; contrastar con ejecución directa del módulo. | RF-01 | Aprobada según propietario | Pendiente |
| REFUGE-06-02 | Campaña y minijuegos | En estado temporal de ensayo recorrer las cinco etapas iniciales, cinco jornadas de preparación y ocho turnos de guerra antes de la decisión final. Registrar opciones, probabilidades, recursos, incidentes y pruebas opcionales; comprobar que no haya excepciones. | RF-02 | Aprobada según propietario; verificar contenido actual de campaña | Pendiente |
| REFUGE-06-03 | Guardado y reanudación | Guardar y salir a mitad de la campaña usando un estado temporal; reabrir con el mismo estado y comparar fase, reservas y estadísticas. Confirmar que los datos queden fuera del repositorio y preservar la partida personal. | RF-03 | Aprobada según propietario | Pendiente |
| REFUGE-06-04 | Arena final | Llegar a la arena y probar flechas y WASD, obstáculos, avisos, daño, salida con Q y agotamiento de vidas. La versión documentada usa una oleada de 40 segundos y dos vidas; confirmar duración y restauración de terminal. | RF-04 | Aprobada en 0.4; expectativas de arena cambiaron en 0.6 | Pendiente |
| REFUGE-06-05 | Desenlaces | En partidas separadas probar sostener el frente, negociar, evacuar y las derrotas previstas por la campaña. Reabrir cada crónica/epílogo guardado y comprobar que no se reinicie el resto del estado. | RF-05 | Aprobada según propietario | Pendiente |
| INT-06-01 | Rutas e integración | Iniciar desde la raíz del checkout y desde /tmp usando la ruta absoluta del proyecto; abrir y cerrar módulos. Confirmar resolución de datos y que la terminal siga usable. Registrar las dependencias de ruta que permanezcan. | INT-01 | Aprobada según propietario | Pendiente |
| ERR-06-01 | Índice/ficha ausentes | Solo en copia de ensayo, apartar temporalmente el índice y una ficha, intentar abrirlos y restaurarlos. Esperados: error controlado, sin cierre inesperado y archivos originales restaurados. | ERR-01 | Aprobada según propietario | Pendiente |
| DEL-06-01 | OVA: exportar/importar | Cuando exista la imagen final, exportar la VM e importarla de forma independiente en VirtualBox. Verificar arranque, cuenta normal, root según configuración real, menú y aplicaciones declaradas. La OVA permanece fuera de Git. | Fuera de la matriz 0.4 | No aplicaba | Pendiente |
| DEL-06-02 | PDF final | Revisar el PDF contra la VM y los archivos reales: versión/logo, aplicaciones, archivos editados, tecnologías, guía de uso, credenciales completadas localmente y enlace a la OVA. No incluir cómics ni credenciales en Git/chats. | Fuera de la matriz 0.4 | No aplicaba | Pendiente |

## Registro por ejecución 0.6

| ID/caso/subcaso | Responsable | SHA, Debian y VM | Dimensión/terminal | Resultado observado | Estado | Fecha ART | Hora ART | Evidencia / incidencia |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | — | — | — | — | Pendiente | — | — | — |

La integración actual del logo tuvo una prueba automatizada de pseudoterminal reportada para 80×24 y 120×40; no es una aprobación manual, no sustituye esta matriz y no prueba la VM del propietario. La OVA y el PDF final no se generaron ni se comprobaron en esta actualización.
