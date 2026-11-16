#!/usr/bin/env bash
# uso: preparar.sh <cena>  — copia o comum, monta o index.html e resolve os tempos do plano.
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; c="$1"; D="$B/cenas/$c"
S=/home/user/tendencias/.claude/skills/estilo-documentario/scripts
cp -r "$B/comum/assets" "$B/comum/estilos" "$D/" ; cp "$B/comum/"{base.css,motor.js,geo.js,biblioteca.js} "$D/"
# só copia imagens VÁLIDAS (um 429 do Wikimedia vem como HTML com nome .jpg)
mkdir -p "$D/img"; rm -f "$D/img/"*.jpg
for f in "$B/imagens/"*.jpg; do [ -f "$f" ] && file "$f" | grep -qE "JPEG|PNG" && cp "$f" "$D/img/"; done
# dimensões reais das imagens: as fotos nascem com a altura certa (a câmera mede antes de a imagem carregar)
python3 -c "
import json,glob,os
from PIL import Image
d={os.path.basename(f):list(Image.open(f).size) for f in glob.glob('$D/img/*.jpg')}
open('$D/imagens.js','w').write('window.IMG = '+json.dumps(d)+';\\n')"
if [ -f "$B/palavras.json" ]; then python3 "$S/resolver_tempos.py" "$B" "$c"; DUR=$(python3 -c "import json;print(json.load(open('$B/cenas.json'))['$c']['dur'])")
else python3 "$B/provisorio.py" "$B" "$c"; DUR=$(python3 -c "import json;print(json.load(open('$D/plano.resolvido.json'))['duracao'])"); fi
TIT=$(python3 -c "import json;print(json.load(open('$D/plano.json')).get('titulo','$c'))")
sed -e "s|{{DUR}}|$DUR|" -e "s|{{TITULO}}|$TIT|" "$B/comum/index.tpl.html" > "$D/index.html"
echo "cena $c pronta (duração $DUR s)"
