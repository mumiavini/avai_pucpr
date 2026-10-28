---
name: canvas
description: Acessa o Canvas da PUCPR (pucpr.instructure.com) via API com o token do .env. Use para listar tarefas e prazos, achar e ler Planos de Ensino (PDF), listar/baixar arquivos e módulos das disciplinas, consultar notas e gerar calendário .ics para o Google Agenda. Também para pedidos informais como "o que vence essa semana", "baixa os arquivos da disciplina X" ou "monta meu calendário da faculdade".
---

# Canvas PUCPR

Repositório: `C:\soft\Personal\Canva`. Python do venv: `.\.venv\Scripts\python.exe`.

## Setup (já feito)
- `.env` tem `CANVAS_TOKEN`; `CANVAS_URL` assume `https://pucpr.instructure.com`.
- Pacotes no venv: `requests`, `tzdata`, `truststore` (proxy corporativo com certificado próprio), `pypdf`.
- Se faltar pacote: `.\.venv\Scripts\python.exe -m pip install <pacote>`.

## Scripts
- `canvas_tasks.py [--all] [--csv arquivo]`: tarefas pendentes por prazo. Importe `get_session()`, `get_all()` e `collect()` para scripts novos; `get_all` já pagina.
- `gen_ics.py`: gera `faculdade.ics` (aulas, provas, entregas e prazos do Canvas). Os dados pessoais (cronograma dos PEs e horários) ficam em `schedule_data.py`, ignorado pelo git; `schedule_data.example.py` é o modelo. Para outro semestre, releia os PEs e atualize `schedule_data.py`.

## Endpoints úteis (`{base}/api/v1/...`)
- `courses?enrollment_state=active` (ignorar itens sem `name`)
- `courses/:id/assignments`, `modules?include[]=items`, `files`, `pages`, `tabs`
- `courses/:id/files/:fid` → campo `url` para baixar o arquivo
- `calendar_events?type=assignment&context_codes[]=course_ID&start_date=&end_date=`
- 403 em `files` ou 404 em `pages` é normal: a disciplina não expõe esse recurso.

## Fluxo para Plano de Ensino
1. Procure PDF com "plano" no nome em `files` ou no módulo "Plano de Ensino".
2. Baixe em `pe/` e extraia o texto com `pypdf`.
3. Leia o cronograma. Datas e horários que o PE não traz devem ser perguntados ao usuário; marque como "data estimada" o que for deduzido.

## Regras
- Nunca imprima, registre ou copie o token. Mostre `.env` só com valores ocultos.
- Somente leitura por padrão. Entregar tarefa, postar em fórum ou qualquer escrita exige confirmação explícita do usuário.
- Dados do Canvas ficam locais; não envie a serviços externos.
- Quando o PE e o Canvas divergirem em uma data, mantenha as duas e avise.
- Responda em português, de forma concisa.
