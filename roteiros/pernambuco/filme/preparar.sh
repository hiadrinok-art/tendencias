#!/usr/bin/env bash
# uso: preparar.sh <cena>  — copia o comum, monta o index.html e resolve os tempos do plano.
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; c="$1"; D="$B/cenas/$c"
S=/home/user/tendencias/.claude/skills/estilo-documentario/scripts
cp -r "$B/comum/assets" "$B/comum/estilos" "$D/" ; cp "$B/comum/"{base.css,motor.js,geo.js,biblioteca.js} "$D/"
[ -d "$B/imagens" ] && mkdir -p "$D/img" && cp -n "$B/imagens/"*.jpg "$D/img/" 2>/dev/null || true
if [ -f "$B/palavras.json" ]; then python3 "$S/resolver_tempos.py" "$B" "$c"; DUR=$(python3 -c "import json;print(json.load(open('$B/cenas.json'))['$c']['dur'])")
else python3 "$B/provisorio.py" "$B" "$c"; DUR=$(python3 -c "import json;print(json.load(open('$D/plano.resolvido.json'))['duracao'])"); fi
TIT=$(python3 -c "import json;print(json.load(open('$D/plano.json')).get('titulo','$c'))")
sed -e "s|{{DUR}}|$DUR|" -e "s|{{TITULO}}|$TIT|" "$B/comum/index.tpl.html" > "$D/index.html"
echo "cena $c pronta (duração $DUR s)"
