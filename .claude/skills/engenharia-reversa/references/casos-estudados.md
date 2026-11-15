# Casos estudados

Estudados em novembro de 2026 a partir do código-fonte (clone raso do branch padrão).

## claude-mem — `thedotmack/claude-mem` (memória entre sessões)
- **Padrão:** Hooks + serviço de fundo (worker local, SQLite; Postgres no modo servidor) + IA para resumir.
- **Fluxo** (`plugin/hooks/hooks.json`):
  - `SessionStart` → `claude-mem start` (sobe o worker) e `hook claude-code context` (injeta memórias relevantes no início)
  - `UserPromptSubmit` → `session-init`
  - `PostToolUse` / `PostToolUseFailure` → `observation` (cada uso de ferramenta vira evento)
  - `PreToolUse` em Read/Bash/Grep/Glob → `file-context` (anexa o que já se sabe sobre o arquivo)
  - `Stop` → `summarize`; `SubagentStop`, `SessionEnd` → fechamento
- **Núcleo:** (1) capturar eventos, (2) um modelo resume em "observações", (3) guardar, (4) devolver as relevantes no `SessionStart`.
- **Detalhe interessante:** `docs/architecture/observer-lifecycle.md` — buffer em RAM limitado (128 msgs/sessão), entrega com prazo de 250 ms, e se o worker cair o evento é descartado de propósito (evita gastar cota reprocessando backlog antigo).
- **Enfeite:** integrações Cursor/Codex/Gemini, dashboard, sync em nuvem, launcher Bun.
- **Riscos:** grava tudo da sessão localmente; resumos gastam tokens.
- **Recriação enxuta (média):** hook `Stop` que pede um resumo curto e anexa em `memoria/AAAA-MM-DD.md`; hook `SessionStart` que imprime os últimos N resumos. Sem worker, sem banco.

## headroom — `chopratejas/headroom` (menos tokens)
- **Padrão:** Proxy (`headroom wrap claude` sobe proxy local e define `ANTHROPIC_BASE_URL`; ver `headroom/cli/wrap.py`). Também tem MCP.
- **Núcleo:** `headroom/transforms/content_router.py` detecta o tipo de conteúdo e manda para um compressor específico: código (preserva AST), arrays JSON (`smart_crusher`), resultados de grep (`search_compressor`), logs de build/teste (`log_compressor`, hoje em Rust), texto (modelo ML).
- **CCR** (`headroom/ccr/`): guarda o original e dá ao modelo uma ferramenta para recuperar o conteúdo completo — compressão reversível.
- **`cache_aligner.py`:** estabiliza o prefixo das mensagens para aproveitar o cache de prompt.
- **Recriação enxuta (difícil para o completo; fácil para 1 parte):** hook `PostToolUse` não reescreve a saída, então o caminho leve é instruir/limitar saídas (ex.: `| tail -50`, `head_limit`). Compressão de verdade exige proxy.

## claude-code-setup — `anthropics/claude-plugins-official/plugins/claude-code-setup`
- **Padrão:** Skill pura (`claude-automation-recommender`, 289 linhas + 5 referências). Autor no `plugin.json`: Anthropic.
- **Fluxo:** Fase 1 analisa o projeto (`package.json`, `pyproject.toml`, `.claude/`, pastas) → Fase 2 tabelas "sinal do código → recomendação" para MCP, skills, hooks, subagentes, plugins.
- **Regra-chave:** é **somente leitura**; recomenda 1–2 por categoria.
- **Recriação (fácil):** mesma skill com tabelas de sinais para fluxo de conteúdo/marketing (Instagram, Canva, Higgsfield, ElevenLabs, Postiz).

## task-observer — `rebelytics/one-skill-to-rule-them-all` (licença CC-BY-4.0)
- **Padrão:** Skill pura grande (753 linhas no core + ~9 mil em `references/`) + scripts bash auxiliares.
- **Núcleo:** durante o trabalho, anota "observações" (correções do usuário, fluxos repetidos, decisões) como arquivos Markdown com frontmatter YAML em `skill-observations/observation-log/`; numa revisão periódica, propõe patches nas skills e **espera aprovação** (stage → diff → aplicar).
- **Detalhes:** protocolo de início de sessão com checklist; workspace deve ficar em caminho estável (não em clone temporário); pede uma linha no `CLAUDE.md` para ativar de forma confiável.
- **Recriação enxuta (fácil):** skill de ~100 linhas em PT-BR: logar observação em `observacoes/` + comando de revisão que gera propostas de edição. Dar crédito (CC-BY exige atribuição).

## OmniRoute — `diegosouzapw/OmniRoute` (não clonado)
- **Padrão:** Proxy/gateway (`localhost:20128`), roteia entre muitos provedores com fallback.
- **Decisão:** não recriar — o valor central é contornar limites trocando de provedor/conta, o que esbarra em termos de uso. A ideia legítima (proxy que troca de modelo) é o mesmo padrão do headroom.
