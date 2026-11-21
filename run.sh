#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$ROOT_DIR/tests"

detect_python() {
    local candidate
    for candidate in python3 python; do
        if "$candidate" --version >/dev/null 2>&1; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 1
}

if [ -n "${PYTHON:-}" ]; then
    PYTHON_BIN="$PYTHON"
elif ! PYTHON_BIN="$(detect_python)"; then
    echo "Не найден интерпретатор Python 3" >&2
    exit 1
fi

usage() {
    cat <<'USAGE'
Использование:
  ./run.sh assemble  -i <программа.json> -o <программа.bin> [-t]
  ./run.sh test
  ./run.sh demo
USAGE
}

run_demo() {
    local output_dir="$ROOT_DIR/output"
    mkdir -p "$output_dir"
    echo "== Тест спецификации (Этап 2) =="
    "$PYTHON_BIN" "$ROOT_DIR/src/assembler.py" \
        -i "$DATA_DIR/spec_tests.json" \
        -o "$output_dir/spec_tests.bin" -t
}

command="${1:-}"
case "$command" in
    assemble)
        shift
        exec "$PYTHON_BIN" "$ROOT_DIR/src/assembler.py" "$@"
        ;;
    test)
        shift
        exec "$PYTHON_BIN" -m unittest discover -s "$ROOT_DIR/tests" -v
        ;;
    demo)
        shift
        run_demo
        ;;
    *)
        usage
        exit 2
        ;;
esac
