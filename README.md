# Alexandria OS

Repositorio privado y fuente de verdad del proyecto: [thiagoalfonsounp-creator/alexandria-os](https://github.com/thiagoalfonsounp-creator/alexandria-os).

Alexandria OS es una distribución personalizada basada en Debian 13 para consultar el universo del cómic principal de *The Walking Dead*, organizar una biblioteca personal y desarrollar una experiencia de supervivencia.

## Estado actual — 7 de noviembre de 2026

- La rama principal es `main`.
- GitHub contiene la documentación `README.md` y `AGENTS.md`. El código ejecutable de la copia instalada en la VM todavía no está sincronizado en este repositorio; `bin/alexandria` y `src/world/menu.sh` aún no están presentes. Por eso, este clon todavía no se puede iniciar como la copia de la VM.
- El usuario ejecutó el paquete actualizado en Debian y confirmó que funciona. En las capturas se ven `WALKER DATABASE` con siete apartados, `FIELD OBSERVATIONS` con FO-001 a FO-003 y el expediente FO-001 con todos sus campos.
- El paquete local también contiene un catálogo y lector de cómics, un cuaderno de campo y el módulo `THE REFUGE` en preparación. Su publicación en GitHub y las verificaciones que no aparecen arriba siguen pendientes.

## Requisitos y ejecución

La implementación actual está preparada para Debian GNU/Linux 13 y utiliza Bash, `dialog` y `nano`. El lector de cómics PDF requiere `poppler-utils` (`pdfinfo` y `pdftoppm`) y `chafa`. `unzip` permite extraer el paquete.

```bash
sudo apt update
sudo apt install bash dialog nano unzip poppler-utils chafa
```

Una vez que el código de la VM se sincronice con el repositorio, el lanzador previsto es:

```bash
cd /home/walker/alexandria-os
./bin/alexandria
```

Los menús se recorren con las flechas y Enter. Escape cancela o vuelve al menú anterior. Algunos scripts asumen `/home/walker/alexandria-os` o `$HOME/alexandria-os`; esas rutas deben ajustarse si se instala con otra ubicación o usuario.

## Biblioteca personal

Los PDF o CBZ deben guardarse localmente en `imports/comics/` y solo deben usarse archivos que tengas derecho a utilizar. No subas cómics protegidos al repositorio ni los incluyas en paquetes compartidos.

## Criterio del archivo

El contenido sobre caminantes se limita al canon del cómic principal. Las escenas, las observaciones de conducta y las declaraciones del autor se mantienen diferenciadas. Los registros usan las etiquetas `CONFIRMED`, `OBSERVED` o `UNCONFIRMED`; los datos no establecidos por las fuentes quedan abiertos.

## Estructura prevista del proyecto

```text
AGENTS.md               Reglas de trabajo, canon y evidencia
README.md               Estado, requisitos, uso e historial
bin/                    Lanzador principal
src/world/              Menús y expedientes de THE WORLD
src/comic_archive/      Catálogo y lector de cómics
data/world/             Expedientes y observaciones en texto
imports/comics/         Archivos personales locales; no se publican
docs/                   Documentación del proyecto
```

Esta estructura describe el paquete local; el código todavía no se encuentra en GitHub.

## Historial de trabajo

### 2026-11-07 — Inicio de la documentación

- Se establecieron `README.md` como registro acumulativo del estado del proyecto y `AGENTS.md` como reglas de trabajo.
- El repositorio privado usa la rama principal `main`.

### 2026-11-07 — Verificación funcional y actualización documental

- El usuario ejecutó el paquete actualizado en la VM Debian y confirmó el funcionamiento de `WALKER DATABASE` y `FIELD OBSERVATIONS`.
- Se detallaron en `AGENTS.md` el criterio de canon, los niveles de evidencia, el esquema de los registros y las reglas de validación.
- Se actualizó este README con la verificación y se aclaró que el código de la VM aún debe sincronizarse con GitHub.
- **Pendiente:** incorporar el código ejecutable de la VM a `main` y documentar las verificaciones futuras.

Al finalizar cada tarea, actualizá el estado y agregá una entrada nueva a este historial sin eliminar las anteriores. No registres credenciales ni afirmes validaciones que no se hayan realizado.
