# Spec: Redesign visual + responsividade + engajamento

**Data:** 2026-06-12
**Projeto:** COPA-SECOM (bolao Copa do Mundo 2026)
**Abordagem aprovada:** CSS puro dentro do Streamlit, sem dependencias novas, sem mudanca de schema.

## Objetivo

Dar upgrade no design do app, torna-lo responsivo (uso meio a meio celular/desktop) e adicionar elementos de engajamento, mantendo a identidade visual Brasil/Copa (azul #002776, amarelo #ffdf00, verde #009c3b) ja existente.

## Restricao inegociavel

**Nenhuma perda de dados.** Sem migracao de banco, sem tabela nova, sem DELETE/UPDATE em massa. Todo recurso novo (estatisticas, setas de ranking, craque da rodada) e calculado em tempo de leitura sobre os dados existentes. Os unicos caminhos de escrita continuam sendo os atuais: salvar palpite (usuario) e salvar placar (admin).

## Escopo

### 1. Visual global (`app.py` — bloco CSS)

- Media queries com breakpoint 640px:
  - Hero compacto no mobile (padding e fonte menores).
  - Match cards com padding reduzido, nomes de times com `text-overflow: ellipsis`.
  - Placar central (`score-wrap`) menor no mobile.
  - Podio do ranking empilhado no mobile, com 1o lugar no topo e maior.
- Alvos de toque: inputs e botoes com altura minima 44px no mobile.
- Animacao de entrada nos cards (fade + slide sutil); efeitos hover apenas em `@media (hover: hover)`.
- Hero header refinado: gradiente mais profundo, subtitulo dinamico com a fase atual do torneio (fase de grupos vs mata-mata, derivada dos jogos cadastrados).

### 2. Pagina Grupos (`modules/ui_dashboard.py`)

- Card de estatisticas pessoais no topo, antes do seletor de data, com 4 metricas:
  - Pontos totais (de `users.total_score`).
  - Posicao no ranking (rank do usuario por `total_score`).
  - Aproveitamento: % de palpites que pontuaram (`points_earned > 0`) sobre palpites em jogos encerrados (FT/AET/PEN).
  - Sequencia atual: jogos encerrados consecutivos (ordem de kickoff, mais recente para tras) em que o usuario pontuou.
- Refinamento dos match cards conforme CSS global.

### 3. Ranking (`modules/ui_ranking.py`)

- **Correcao de bug:** coluna "Exatos" conta `points_earned == 3`; correto e `points_earned == 5` (placar exato vale 5 pts desde a mudanca de pontuacao). Correcao apenas na consulta de exibicao; nao altera pontos gravados.
- Setas de movimento: comparar ranking atual com ranking recalculado excluindo os jogos do ultimo dia (data BRT) com jogos encerrados. Subiu = seta verde; caiu = seta vermelha; manteve = neutro. Se nao ha dia anterior para comparar, ocultar setas.
- "Craque da rodada": usuario com mais pontos somados nos jogos do ultimo dia encerrado; badge dourado ao lado do nome. Empate: todos os empatados recebem o badge.
- Substituir `st.dataframe` por linhas estilizadas em HTML/CSS responsivas (a tabela pandas quebra no mobile). Destaque da linha do usuario logado mantido.

### 4. Painel Admin (`modules/ui_admin.py`)

- Polimento visual apenas; fluxo de salvar identico.
- Status dos jogos indicado por cor (borda/badge) em vez de emoji.
- Contador no topo: "X de 72 jogos com placar lancado" (jogos com status FT/AET/PEN na fase de grupos; mata-mata contado a parte quando existir).

### 5. Fora de escopo

- Qualquer mudanca de schema ou nova tabela.
- Novas dependencias Python.
- Mudanca nas regras de pontuacao ou no fluxo de palpites.
- Reescrita fora do Streamlit.

## Decisoes tecnicas

- "Ultima rodada" para setas e craque da rodada = ultimo dia-calendario (BRT) que possui pelo menos um jogo encerrado. Nao depende do conceito de Rodada 1/2/3 do admin, funcionando tambem no mata-mata.
- Estatisticas calculadas por consulta a cada render; volume de dados e pequeno (dezenas de usuarios, 72+ jogos), sem necessidade de cache.
- CSS continua centralizado no bloco unico de `app.py` para evitar duplicacao entre modulos.

## Verificacao

- App rodado localmente com banco de desenvolvimento.
- Telas testadas via Playwright em viewport mobile (390x844) e desktop (1280x800): Grupos, Ranking, Mata-Mata, Admin.
- Conferir que pontos exibidos nao mudaram para nenhum usuario (a correcao dos Exatos muda apenas a contagem exibida, nao os pontos).
- Deploy: push para GitHub aciona o Streamlit Cloud automaticamente (feito pelo usuario apos validacao).
