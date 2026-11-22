# Paso 1. Terminal, Git y flujo de trabajo

![Dónde estás](diagrams/where.svg)

Este paso toma unos 60 minutos.

## Antes de empezar

1. Abre `.github/workflows/step-1.yml`: ¿qué comando corre y qué lo pone en rojo?
2. ¿Por qué conviene separar un cambio en una rama nueva y abrir un Pull Request en lugar de empujar commits directo a `main`?
3. ¿Qué diferencia a una historia de usuario verificable de una petición ambigua cuando un equipo planea un cambio?

## Por qué importa

En el posgrado entregarás cada proyecto en un Pull Request, y el CI decidirá si pasa. Si no sabes leer un script ni por qué un job quedó en rojo, perderás horas en lo que no es el curso.

## Lo mínimo que necesitas saber

- **Terminal.** `cd carpeta` entra a una carpeta, `ls` lista lo que hay y `cat archivo` muestra su contenido. Un script se corre con `./script.sh argumento` si tiene permiso de ejecución (`chmod +x`).
- **Salida y errores.** Un programa escribe resultados en la salida estándar y errores en la de errores (`>&2` en bash), y termina con un código: `0` si todo salió bien y otro número si falló. `echo $?` muestra el código del último comando, y CI usa ese código para decidir si un paso pasa.
- **Columnas con `awk`.** `awk '{print $3}' archivo` imprime la tercera columna de cada línea, separada por espacios. Es la herramienta que usa `log_report.sh` para leer `data/access.log`.
- **Commit.** Una foto del proyecto con un mensaje que explica el cambio. `git add archivo` elige qué entra en la foto y `git commit -m "mensaje"` la toma.
- **Rama.** Una línea de trabajo aparte. `git switch -c fix/step-1-log-report` crea una rama y te mueve a ella; tus commits no tocan `main` hasta que alguien los acepte.
- **Push.** `git push -u origin fix/step-1-log-report` sube tu rama a GitHub. La primera vez, `-u` conecta tu rama local con la remota.
- **Pull Request.** En GitHub, el botón **Compare & pull request** que aparece después del push abre la propuesta de llevar tu rama a `main`. Ahí otra persona revisa el diff y comenta.
- **Ver qué pasa.** `git status` muestra qué cambió y qué está listo para el commit, y `git log --oneline` muestra la historia.

## Qué vas a hacer

- **Leer**. Inspecciona `scripts/log_report.sh` y las primeras líneas de `data/access.log` para entender el formato de columnas y cómo se encadenan `wc`, `awk`, `sort` y `uniq`. Si quieres repasar comandos básicos del shell, abre [example/intro-terminal.md](example/intro-terminal.md).
- **Debuguear**. Crea una rama nueva y corre `./scripts/log_report.sh data/access.log`, luego `./scripts/log_report.sh` sin argumento y con un archivo que no existe. Compara `errors_5xx` con lo que cuentas a mano en el log, y lee el error que sale cuando falta el archivo: ¿le serviría a quien lo encuentra a las 3 a. m. en un job de CI? Corrige las dos fallas.
- **Escribir**. Completa la historia de usuario en `docs/stories/001-order-history.md` usando el formato Como / Quiero / Para y al menos dos criterios Dado / Cuando / Entonces. Luego abre tu Pull Request y contrasta tu trabajo contra la guía de [examples/code-review.md](../../examples/code-review.md).

![Flujo Git](diagrams/git-flow.svg)

## Criterios de aceptación

- `CA-1.1` `scripts/log_report.sh` tiene permiso de ejecución (`+x`). Si no recibe argumento o el archivo no existe, imprime en stderr `Error: log file not found: <archivo>` y sale con código `1`. Si el archivo existe, sale con código `0`.
- `CA-1.2` `scripts/log_report.sh data/access.log` imprime `total_requests`, `errors_5xx` y `top_endpoints` con los conteos exactos del log.
- `CA-1.3` `docs/stories/001-order-history.md` cumple la estructura Como / Quiero / Para e incluye al menos dos criterios, cada uno en una línea con Dado, Cuando y Entonces en ese orden. El check solo revisa esas palabras; el contenido lo revisas tú con [examples/historia-y-pr.md](../../examples/historia-y-pr.md).

## Al terminar

1. `log_report.sh` corre cada noche en un job de CI y una noche el archivo no existe. ¿Qué pasa con el pipeline si el script sale con `0` y qué pasa si sale con `1`?
2. Escribe un criterio Dado / Cuando / Entonces para "el reporte ignora las líneas vacías del log". ¿Cómo lo comprobarías con un test?
3. Explica en tres líneas, con tus palabras, qué cambiaste y por qué. Si no puedes, vuelve a la pista 1 antes de seguir.

## Cómo verificar

Ejecuta `make check STEP=1` desde la raíz del repositorio para validar los tres criterios en automático. Si te trabas, revisa los ejemplos en [example/intro-terminal.md](example/intro-terminal.md) y [example/sample_report.sh](example/sample_report.sh), o abre la [primera pista](hints/1.md).

## Respuestas de autoevaluación

1. Con `0`, el pipeline sigue en verde y publica un reporte vacío; nadie se entera hasta que alguien lo lee. Con `1`, el job queda en rojo y avisa esa misma noche.
2. Dado un log con una línea vacía al final, Cuando corro `log_report.sh`, Entonces `total_requests` no cuenta esa línea. El test crea un archivo temporal con esa línea y compara el conteo contra el mismo log sin ella.
3. Respuesta personal. Debe mencionar el código de salida para el archivo faltante y el patrón que ahora cuenta solo los códigos que empiezan con 5.
