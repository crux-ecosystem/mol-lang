#!/bin/bash
# MOL Docker Entrypoint
# Usage:
#   docker run mol                          → starts playground on :8000
#   docker run mol run program.mol          → runs a .mol file
#   docker run mol repl                     → interactive REPL
#   docker run mol version                  → shows version
#   docker run mol transpile file.mol -t py → transpiles

set -e

case "${1:-playground}" in
  playground)
    echo ""
    echo "  🟣 MOL Playground starting on http://0.0.0.0:8000"
    echo ""
    exec python -m uvicorn playground.server:app --host 0.0.0.0 --port 8000
    ;;
  run|repl|version|parse|transpile)
    exec mol "$@"
    ;;
  help|--help|-h)
    echo ""
    echo "  MOL — The Cognitive Programming Language"
    echo ""
    echo "  Usage:"
    echo "    docker run mol                        Start playground on :8000"
    echo "    docker run mol run <file.mol>          Run a .mol program"
    echo "    docker run mol repl                    Interactive REPL"
    echo "    docker run mol version                 Show version"
    echo "    docker run mol transpile <file> -t py  Transpile to Python"
    echo ""
    echo "  Mount your files:"
    echo "    docker run -v \$(pwd):/code mol run /code/program.mol"
    echo ""
    ;;
  *)
    exec "$@"
    ;;
esac
