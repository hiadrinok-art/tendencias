#!/usr/bin/env bash
# uso: conferir_cena.sh <cena> <tempos separados por vírgula> — prepara, lint, validate (erros JS/arquivos faltando) e capturas
set -uo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; c="$1"; HF=/tmp/claude-0/-home-user-tendencias/ff0bb95c-1b54-510c-87fb-b7386b7e16e7/scratchpad/hf/node_modules/.bin/hyperframes
"$B/preparar.sh" "$c" >/dev/null || exit 1
cd "$B/cenas/$c"
$HF lint . 2>&1 | grep -v -i telemetr | grep -E "✗|errors" | head -5
$HF validate . 2>&1 | grep -v -i telemetr | grep -E "✗|error\(s\)" | head -8
[ -n "${2:-}" ] && rm -rf "$B/conf/$c" && timeout 400 $HF snapshot . --at "$2" -o "$B/conf/$c" --no-end 2>&1 | grep contact
