# Guía práctica opcional de terminal

Si ya te mueves con soltura en Bash o Zsh, puedes saltar esta guía e ir directo al Paso 1. Si prefieres afianzar los comandos base, prueba cada bloque en la terminal de tu Codespace.

## 1. Dónde estás y cómo moverte

Toda terminal mantiene un directorio actual de trabajo. Usa rutas relativas cuando partes desde donde estás y rutas absolutas cuando inicias desde `/` o `$HOME`.

```bash
pwd                     # Imprime la ruta completa actual
ls -la                  # Lista archivos, permisos y archivos ocultos
cd steps/01-terminal-git
cd ../..                # Regresa dos niveles arriba
```

## 2. Inspeccionar archivos y conectar comandos con pipes

El operador `|` toma la salida estándar (`stdout`) de un programa y la entrega como entrada estándar (`stdin`) del siguiente. Así compones tareas pequeñas sin crear archivos temporales.

```bash
head -n 10 README.md
wc -l README.md
find steps -name "README.md" | sort
```

Cada comando termina con un código de salida (`$?`). El valor `0` indica éxito y cualquier valor distinto de `0` indica error.

```bash
ls README.md > /dev/null
echo $?    # Imprime 0

ls archivo_que_no_existe 2> /dev/null
echo $?    # Imprime un número distinto de 0
```

## 3. Hacer ejecutable un script

Todo script de Bash lleva un *shebang* en la primera línea (`#!/usr/bin/env bash`), modo estricto (`set -euo pipefail`) y permiso de ejecución.

```bash
chmod +x steps/01-terminal-git/example/sample_report.sh
./steps/01-terminal-git/example/sample_report.sh data/products.csv
```

Con estos tres bloques cubres todo lo necesario para resolver el Paso 1.
