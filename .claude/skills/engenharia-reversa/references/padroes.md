# Padrões de arquitetura de ferramentas para Claude Code

| Padrão | Como reconhecer | Como funciona | Custo de recriar |
|---|---|---|---|
| **Skill pura** | Só `SKILL.md` + `references/` | Frontmatter `description` decide quando o Claude carrega; corpo é instrução. Referências carregam sob demanda. | Fácil |
| **Hooks** | `hooks/hooks.json` | Eventos: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionEnd`. O script recebe JSON no stdin; o que imprime no stdout em `SessionStart`/`UserPromptSubmit` vira contexto. Exit code 2 em `PreToolUse` bloqueia a ferramenta. | Fácil/Média |
| **Proxy** | Menciona `ANTHROPIC_BASE_URL` | Servidor local recebe a requisição da API, modifica (comprime, troca modelo, loga) e repassa. | Difícil |
| **MCP server** | `.mcp.json` ou `mcp_server.py` | Processo que expõe ferramentas novas ao Claude via protocolo MCP. | Média |
| **Serviço de fundo** | `worker`, `server/`, banco SQLite/Postgres | Hooks só entregam eventos ao serviço; ele processa (às vezes com IA) e guarda. | Difícil |

## Dicas de leitura rápida
- `find . -type f -not -path './.git/*' -not -path '*/node_modules/*' | head -80`
- `wc -l` nos arquivos centrais para saber o tamanho real
- Procurar a docstring do módulo principal: geralmente explica a arquitetura
- `grep -rn "ANTHROPIC_BASE_URL\|hooks.json\|SKILL.md"` revela o padrão rápido
