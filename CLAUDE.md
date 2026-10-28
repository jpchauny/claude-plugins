# CLAUDE.md

## Carpeta `research/` — acceso restringido (2026-10-22)

No leer, buscar, listar, editar ni mover nada dentro de `research/`
sin permiso explícito del usuario. Si una tarea lo requiere, pedir
permiso antes, diciendo qué archivo y para qué. El permiso vale solo
para ese pedido, no para los siguientes.

En búsquedas por el repo (grep, find, Explore), excluir `research/`.

## Desarrollo de la app (2026-10-22)

Esta app se desarrolla con spec-driven development: antes de cambiar
cualquier cosa, seguir [specs/development.md](specs/development.md).

## El qué y el cómo (2026-10-28)

El usuario dice el qué: el comportamiento que se ve desde afuera.
Claude decide el cómo: formatos, algoritmos, scripts, mensajes, campos,
estructura del código y de las specs. No preguntar detalles de
implementación; decidirlos, escribirlos en la spec y seguir. Preguntar
solo lo que cambia lo que el usuario ve o decide.
