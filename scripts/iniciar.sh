#!/usr/bin/env bash
# Inicia o Radar numa hospedagem (Render, Railway...): sobe o site e, em
# segundo plano, coleta os editais do PNCP agora e depois uma vez por dia.
set -euo pipefail
mkdir -p "$(dirname "${RADAR_BANCO:-dados/radar.db}")"

(
  while true; do
    python -m radar.coletor --dias "${RADAR_DIAS_COLETA:-4}" || echo "Coleta falhou; tento de novo depois."
    sleep 86400
  done
) &

exec uvicorn radar.app:app --host 0.0.0.0 --port "${PORT:-8000}" --no-server-header --no-proxy-headers
