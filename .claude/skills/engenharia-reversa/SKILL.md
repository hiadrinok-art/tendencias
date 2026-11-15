---
name: engenharia-reversa
description: Método para fazer engenharia reversa de ferramentas, plugins, skills e apps (principalmente do ecossistema Claude Code) — descobrir como funcionam por dentro e recriar uma versão própria, mais enxuta e em PT-BR. Use quando o usuário pedir "engenharia reversa", "como isso funciona por dentro", "recria isso", "faz uma versão nossa de X", ou mandar print/link de uma ferramenta que quer entender ou copiar a ideia.
---

# Engenharia Reversa

Objetivo: entender **o mecanismo** de uma ferramenta (não só o marketing) e,
se fizer sentido, recriar a ideia numa versão própria, menor e adaptada.

## Regras de limite (antes de tudo)

- **Código aberto:** pode estudar e recriar. Confira a licença (MIT, Apache,
  CC-BY...) e dê crédito ao original quando copiar trechos ou estrutura.
- **Código fechado:** estude só o comportamento observável (docs, saídas, tráfego
  próprio). Não quebrar ofuscação, DRM, licenciamento ou proteção anticópia.
- **Não recriar** o que só existe para burlar limites, termos de uso,
  cobrança ou segurança (ex.: rodízio de contas gratuitas para fugir de limite).
- **Não copiar marca:** a versão recriada tem nome, visual e textos próprios.

## Método em 6 passos

1. **Promessa → hipótese.** Traduza o slogan numa pergunta técnica.
   "Memória entre sessões" → *onde ele grava, quando grava, como devolve?*
2. **Achar a fonte oficial.** Buscar o repo original (desconfiar de forks com o
   mesmo nome). Clonar raso no scratchpad: `git clone --depth 1 <url>`.
   Nunca executar scripts do repo clonado — só ler.
3. **Mapear a superfície.** Ler primeiro os arquivos que revelam a arquitetura:
   - Plugin Claude Code: `.claude-plugin/plugin.json`, `hooks/hooks.json`,
     `skills/*/SKILL.md`, `commands/`, `agents/`, `.mcp.json`
   - Python: `pyproject.toml` (entry points), `cli/`
   - Node: `package.json` (`bin`, `scripts`)
   - Docs de arquitetura: `docs/architecture/`, `AGENTS.md`, `CLAUDE.md`
4. **Identificar o padrão.** Quase toda ferramenta de IA cai num destes
   (detalhes em `references/padroes.md`):
   - **Skill pura** (só instruções em Markdown)
   - **Hooks** (scripts disparados em eventos da sessão)
   - **Proxy** (fica entre o cliente e a API via `ANTHROPIC_BASE_URL`)
   - **MCP server** (expõe ferramentas novas)
   - **Serviço de fundo** (worker + banco local)
5. **Separar núcleo de enfeite.** Descobrir os ~20% que entregam o valor.
   O resto costuma ser compatibilidade, telemetria, dashboards, multi-plataforma.
6. **Recriar enxuto.** Escolher o padrão mais simples que entrega o núcleo
   (preferir skill > hooks > MCP > proxy > serviço). Escrever em PT-BR, testar
   num projeto real e documentar o que ficou de fora e por quê.

## Entregável padrão

Ao terminar uma análise, responder com:
- **O que promete** vs **o que realmente faz** (com arquivo:linha de prova)
- **Padrão** usado e **fluxo** (evento → ação → resultado)
- **Núcleo** em 3–5 itens
- **Riscos** (privacidade, custo de tokens, termos de uso)
- **Plano de recriação** com dificuldade (fácil / média / difícil)

## Casos já estudados

Ver `references/casos-estudados.md` (claude-mem, headroom, claude-code-setup,
task-observer, OmniRoute). Antes de reestudar um desses, ler o caso — e só
re-clonar se precisar de detalhe novo ou se a versão mudou.
Ao estudar uma ferramenta nova, **acrescentar o caso nesse arquivo**.
