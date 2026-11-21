# Fork nandomoreirame/beaverhabits

Fork pessoal do [Beaver Habit Tracker](https://github.com/daya0576/beaverhabits) para rodar no homelab em `https://habitos.home.nandomoreira.me`. O upstream não tem tradução, usa a Roboto padrão do Quasar e a API dele exige uma requisição por hábito para montar o dia, o que não serve a um widget de barra.

As mudanças ficam em módulos novos para que o `git merge upstream/main` gere o mínimo de conflito.

## O que o fork muda

| Mudança | Onde |
|---|---|
| Fontes Inter (texto) e JetBrains Mono (datas e números), servidas localmente | `beaverhabits/frontend/fonts.py`, `statics/fonts/` |
| Interface em pt-BR com `LANGUAGE=pt-BR`; sem a variável, continua em inglês | `beaverhabits/i18n.py`, `beaverhabits/locales/pt_BR.json` |
| API estendida para widgets de desktop | `beaverhabits/routes/api_ext.py`, `beaverhabits/core/summary.py` |
| Deploy no homelab | `compose.yml`, `bin/deploy`, `deploy/Caddyfile.snippet` |

## API estendida

Base `/api/v1/ext`, autenticação `Authorization: Bearer <token>` (token permanente gerado em `/gui/tokens`). Datas em ISO (`YYYY-MM-DD`). Sem `date`, vale o dia atual no fuso `TIME_ZONE`.

| Método | Rota | Resposta |
|---|---|---|
| `GET` | `/today?date=` | `{date, total, done, habits: [{id, name, star, tags, done, note, streak}]}` com os hábitos ativos na ordem do app |
| `POST` | `/ticks` | corpo `{ticks: [{habit_id, date, done, text?}]}` com 1 a 100 itens; um id desconhecido devolve 404 e nada é gravado |
| `GET` | `/habits/{id}/summary?date=` | `{id, name, date, streak, longest_streak, last_7_days, last_30_days, total, last_done}` |

`streak` conta os dias seguidos até hoje; enquanto o dia não termina, um hábito ainda não marcado hoje mantém a sequência de ontem.

```bash
T=$(cat ~/.config/beaverhabits/token)
curl -s -H "Authorization: Bearer $T" https://habitos.home.nandomoreira.me/api/v1/ext/today
```

As rotas originais (`/api/v1/habits`, criar, editar, arquivar, excluir) continuam iguais; o Swagger fica em `/docs`.

## Tradução

O texto em inglês é a chave do catálogo: string nova sem tradução aparece em inglês, nunca quebra. Para traduzir, envolva o texto com `t("...")` (placeholders com `t("{days} days ago", days=n)`) e adicione a entrada em `beaverhabits/locales/pt_BR.json`. O teste `tests/test_i18n.py` falha se uma tradução vier vazia ou perder um placeholder. Componentes do Quasar (calendário) usam o pacote de idioma do próprio Quasar.

## Desenvolvimento

```bash
uv sync
DATABASE_URL="sqlite+aiosqlite:///:memory:" HABITS_STORAGE="USER_DISK" uv run pytest -q
LANGUAGE=pt-BR uv run ./start.sh dev   # http://localhost:9001/demo
```

Não rode `black` em arquivos do upstream: a versão local reformata linhas que não são do fork e gera conflito no merge. Formate só os arquivos novos.

## Deploy

```bash
./bin/deploy
```

Roda os testes, sincroniza o repositório com `homelab:beaverhabits/` por `rsync` e reconstrói o contêiner. O `rsync` nunca toca `data/` (banco SQLite) nem `.env` (segredos) no homelab. A rota do Caddy está em `deploy/Caddyfile.snippet` e só precisa ser colada uma vez.

## Atualizar a partir do upstream

```bash
git fetch upstream
git merge upstream/main
```

Conflitos esperados: strings novas ou alteradas nos arquivos de interface (envolva com `t()` e traduza) e o `ui.run_with` em `beaverhabits/routes/routes.py`.

## Segurança

- O contêiner publica só `127.0.0.1:4193`. O Caddy serve em `https://habitos.home.nandomoreira.me`, que só resolve no Pi-hole da LAN e da Tailnet; o certificado vem de DNS-01, sem porta aberta para a internet.
- Autenticação do próprio app: login por senha na interface e Bearer token (JWT ou token permanente) na API. `MAX_USER_COUNT=1` fecha o cadastro depois da primeira conta.
- `NICEGUI_STORAGE_SECRET` e `JWT_SECRET` ficam no `.env` do homelab (permissão 600), gerados no próprio host e fora do git.
- A API estendida valida tudo com Pydantic: lote de 1 a 100 marcações, nota limitada a `DAILY_NOTE_MAX_LENGTH` e id de hábito de até 64 caracteres. Cada usuário só enxerga a própria lista.
- As fontes são servidas pelo próprio app; nenhuma requisição sai para Google Fonts ou CDN.
- `/docs` e `/demo` do upstream continuam abertos, mas só dentro da LAN e da Tailnet.
