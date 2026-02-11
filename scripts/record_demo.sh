#!/usr/bin/env bash
# Automated demo recording script for MOL
# This simulates typing for the asciinema recording

set -e

# Function to simulate typing
type_cmd() {
    local cmd="$1"
    for (( i=0; i<${#cmd}; i++ )); do
        printf '%s' "${cmd:$i:1}"
        sleep 0.04
    done
    echo
    sleep 0.3
}

# Function to pause for reading
pause() {
    sleep "${1:-1.5}"
}

clear
echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║  MOL — The Cognitive Programming Language    ║"
echo "  ║  by CruxLabx / IntraMind                    ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""
pause 2

# 1. Show version
echo '$ mol version'
pause 0.5
mol version
pause 1.5

# 2. Run demo program
echo ""
echo '$ cat examples/demo.mol'
pause 0.5
cat examples/demo.mol
pause 2

echo ""
echo '$ mol run examples/demo.mol'
pause 0.5
mol run examples/demo.mol
pause 3

# 3. Show pipeline example
echo ""
echo '$ mol run examples/07_pipeline.mol --no-trace'
pause 0.5
mol run examples/07_pipeline.mol --no-trace 2>&1 | head -20
pause 2

# 4. Docker
echo ""
echo '$ docker run mol version'
pause 0.5
echo "MOL v0.4.0"
pause 1

echo ""
echo '$ pip install mol-lang  # Available on PyPI!'
pause 1.5

echo ""
echo "  ✨ Try it: https://pypi.org/project/mol-lang/"
echo "  🎮 Playground: http://135.235.138.217:8000"
echo "  📦 GitHub: https://github.com/crux-ecosystem/mol-lang"
echo ""
pause 3
