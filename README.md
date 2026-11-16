# Radar de Editais

Encontra, filtra e resume licitações públicas do PNCP para o ramo de cada empresa.

- `radar/`: API (FastAPI) com contas, sessões e a camada de segurança.
- `radar/coletor.py`: busca editais no PNCP e classifica por ramo (`radar/classificador.py`).
- `radar/site/`: o site (landing, cadastro, login, painel e detalhe do edital), servido pela própria API.
- `tests/`: testes automatizados (`python -m pytest -q`).
- [SEGURANCA.md](SEGURANCA.md): como a API protege contas e dados, LGPD e como rodar.

## Rodar o protótipo

```bash
pip install -r requirements.txt
export RADAR_SEGREDO="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export RADAR_BANCO=dados/radar.db RADAR_HTTPS=0 RADAR_ORIGENS=http://localhost:8000
mkdir -p dados
python -m radar.coletor --dias 4          # baixa os editais dos últimos 4 dias (alguns minutos)
uvicorn radar.app:app --port 8000 --no-server-header --no-proxy-headers
```

Abra http://localhost:8000, cadastre um ramo e veja os editais. Para manter os dados atualizados, rode o coletor uma vez por dia (cron).
