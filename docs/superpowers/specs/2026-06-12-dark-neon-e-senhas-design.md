# Spec: Dark Mode Neon + Gestao de Senhas

**Data:** 2026-06-12
**Status:** Aprovado (usuario delegou decisoes de design; revisao final em producao)

## Objetivo

Duas frentes independentes, entregues juntas:

1. **Gestao de senhas** — admin redefine senha de quem esqueceu; usuario troca a propria senha.
2. **Redesign "Dark Mode Neon"** — fundo escuro com acentos neon, clima de estadio, cantos arredondados com brilho, bandeiras maiores e tipografia esportiva.

## Parte 1 — Gestao de senhas

### Contexto

Senhas usam bcrypt (`modules/auth.py`) — irrecuperaveis por design. Nao ha e-mail no cadastro, entao fluxo "esqueci minha senha" autonomo e inviavel; o reset passa pelo admin.

### Novas funcoes em `modules/auth.py`

- `change_password(user_id, current_password, new_password) -> tuple[bool, str]`
  Valida senha atual com `verify_password`; exige nova senha com minimo 6 caracteres (mesma regra do cadastro); grava novo hash.
- `admin_reset_password(username) -> tuple[bool, str]`
  Gera senha temporaria legivel no formato `copa-XXXX` (4 caracteres de `secrets.choice` sobre alfabeto sem ambiguos: `abcdefghjkmnpqrstuvwxyz23456789`), grava o hash e retorna a senha em claro na mensagem para o admin repassar.

Sem coluna nova no banco. Sem flag "deve trocar no proximo login" (YAGNI — grupo pequeno e conhecido).

### UI

- **Pagina "Conta"** (novo `modules/ui_account.py`, item "Conta" na navegacao da sidebar): formulario com senha atual, nova senha e confirmacao. Mensagens de erro/sucesso inline.
- **Painel Admin** (`modules/ui_admin.py`): nova secao "Usuarios" no topo (expander): selectbox com todos os usuarios + botao "Gerar senha temporaria". A senha gerada aparece uma unica vez em `st.code` para copiar.

### Testes (pytest, sem banco)

- Roundtrip `hash_password`/`verify_password` (ja implicito, formaliza).
- Gerador de senha temporaria: formato `copa-` + 4 chars do alfabeto permitido; duas chamadas geram valores distintos.
- Validacao de nova senha (tamanho minimo, confirmacao) extraida como funcao pura `validate_new_password(new, confirm) -> str | None` para ser testavel.

## Parte 2 — Dark Mode Neon

### Paleta

| Papel | Cor |
|---|---|
| Fundo base | `#0a0f1e` (azul-noite quase preto) |
| Fundo secundario / cards | `#121a2e` com borda `rgba(255,255,255,0.08)` |
| Neon primario (acoes, destaques) | verde neon `#00ff87` |
| Neon secundario (titulos, badges) | amarelo eletrico `#ffe600` |
| Neon de apoio (info, links) | ciano `#22d3ee` |
| Texto principal | `#e7ecf5` |
| Texto secundario | `#8b96ad` |

Mantem identidade Brasil (verde/amarelo/azul) em versao neon.

### Tema Streamlit (`.streamlit/config.toml`)

`base = "dark"`, `primaryColor = "#00ff87"`, `backgroundColor = "#0a0f1e"`, `secondaryBackgroundColor = "#121a2e"`, `textColor = "#e7ecf5"` — para inputs, tabs, selectbox e expanders nativos acompanharem o tema. Mesmos valores replicados nos secrets do Streamlit Cloud nao sao necessarios (config.toml versionado vale no deploy).

### Fundo "estadio" (CSS-only, sem imagens externas)

No `.stApp`: camadas de `radial-gradient` simulando refletores (dois focos de luz fria vindos do topo, verde e ciano bem sutis sobre `#0a0f1e`) + `repeating-linear-gradient` vertical muito sutil simulando as faixas do gramado. `background-attachment: fixed` no desktop; sem fixed no mobile (custo de scroll).

### Tipografia

- Corpo: Inter (mantida).
- Display: **Rajdhani** (Google Fonts, pesos 600/700) para titulo do hero, numeros de placar, valores de estatistica, posicoes do ranking e cabecalhos de rodada — visual de placar eletronico esportivo.

### Componentes (CSS em `app.py`, mesmo bloco unico)

- **match-card**: fundo `#121a2e`, raio 16px, borda 1px translucida; hover com `box-shadow` verde neon (`0 0 24px rgba(0,255,135,0.18)`) e borda acesa. Header do card mais escuro (`#0d1426`).
- **score-wrap**: placar estilo painel eletronico — fundo quase preto, dígitos Rajdhani amarelo `#ffe600` com `text-shadow` de brilho.
- **Bandeiras**: usar `flag_img` (Twemoji `<img>`, ja existente e compativel com Windows) nos cards da fase de grupos e do mata-mata. 40px desktop, 30px mobile, com leve `drop-shadow`. Hoje os cards nao exibem bandeira nenhuma.
- **Botoes**: raio 12px; primario verde neon com texto escuro e glow; hover intensifica o glow.
- **Badges de pontos (pts-5/3/1/0)**: versoes dark — fundo translucido da cor neon + texto na cor cheia.
- **stats-card / podio / rank-row / hero**: fundos escuros, acentos neon, glow nos elementos de destaque (1º lugar com borda amarela brilhante).
- **Sidebar**: gradiente azul-noite mais escuro que o atual, borda direita verde neon, botao ativo verde neon.
- **locked-card / countdown / saved-badge**: variantes dark translucidas.
- **ui_auth.py**: header da tela de login adaptado (titulo amarelo neon, subtitulo `#8b96ad`).

### O que NAO muda

- Estrutura das paginas, navegacao, regras de pontuacao, banco, modulos de dados.
- `modules/stats.py` e testes existentes.
- Layout mobile 640px continua (valores adaptados ao novo tema).

## Verificacao

1. `pytest` — 22 testes existentes + novos de senha passam.
2. Import smoke de todos os modulos alterados.
3. App local + screenshot Playwright da tela de login (unica tela que renderiza sem banco — rede do escritorio bloqueia porta 5432).
4. Revisao final do usuario em producao apos push (deploy automatico).

## Riscos

- CSS sobre classes internas do Streamlit pode variar entre versoes — mitigado usando `data-testid` (como ja se faz hoje).
- Contraste: garantir texto `#e7ecf5` sobre `#121a2e` (razao > 10:1); neon so em destaque, nunca em texto longo.
- Admin reset expoe senha temporaria na tela do admin — aceitavel (admin e a pessoa de confianca; senha de uso unico ate o usuario trocar).
