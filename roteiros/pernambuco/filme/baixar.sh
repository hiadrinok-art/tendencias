#!/usr/bin/env bash
# uso: baixar.sh destino.jpg "Nome_do_Arquivo.jpg" [largura]
dest="$1"; n="${2// /_}"; w="${3:-1280}"   # larguras PADRÃO (960, 1280, 1920): as outras dão 429
h=$(printf %s "$n" | md5sum | cut -c1-32)
enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$n")
for url in "https://upload.wikimedia.org/wikipedia/commons/thumb/${h:0:1}/${h:0:2}/$enc/${w}px-$enc" "https://upload.wikimedia.org/wikipedia/commons/${h:0:1}/${h:0:2}/$enc"; do
  for tent in 1 2 3 4 5; do
    code=$(curl -sS -A "estilo-documentario/0.1 (uso pessoal)" -o "$dest" -w "%{http_code}" "$url")
    if [ "$code" = 200 ] && file "$dest" | grep -qiE "JPEG|PNG"; then echo "ok $dest ($(file -b "$dest" | grep -oE '[0-9]+ ?x ?[0-9]+' | tail -1))"; exit 0; fi
    [ "$code" = 404 ] && break
    sleep $((tent*20))
  done
done
echo "FALHOU $dest ($code)"; rm -f "$dest"; exit 1
