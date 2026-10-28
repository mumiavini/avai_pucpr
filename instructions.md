# Como configurar o token do Canvas

O script acessa o Canvas com um **token de acesso pessoal (PAT)**. Ele dá os mesmos acessos que a sua conta, então trate como uma senha.

## 1. Gerar o token
1. Entre no Canvas da sua instituição (ex.: `https://SUA-INSTITUICAO.instructure.com`).
2. Clique em **Conta** (menu à esquerda) e depois em **Configurações**.
3. Role até **Integrações aprovadas** e clique em **+ Novo token de acesso**.
4. Preencha:
   - **Finalidade:** por exemplo, `Script de tarefas`.
   - **Expira em:** recomendado definir uma data (o token fica inválido depois dela).
5. Clique em **Gerar token**.
6. **Copie o token agora.** Ele só aparece uma vez; depois só dá para gerar outro.

## 2. Salvar o token
Crie um arquivo `.env` na raiz do repositório (ele já está no `.gitignore` e não vai para o GitHub):

```
CANVAS_TOKEN=cole_o_token_aqui
CANVAS_URL=https://SUA-INSTITUICAO.instructure.com
```

- Sem aspas e sem espaços ao redor do `=`.
- `CANVAS_URL` é opcional se o valor padrão do script já for o da sua instituição.

Alternativa, só para a sessão atual do PowerShell:

```powershell
$env:CANVAS_TOKEN="cole_o_token_aqui"
$env:CANVAS_URL="https://SUA-INSTITUICAO.instructure.com"
```

## 3. Testar
```powershell
.\.venv\Scripts\python.exe canvas_tasks.py
```

Se aparecer a lista de tarefas, está funcionando.

## Problemas comuns
| Mensagem | Causa e solução |
|---|---|
| `Token inválido, expirado ou revogado (401)` | Gere um novo token e atualize o `.env`. |
| `Defina as variáveis de ambiente CANVAS_TOKEN e CANVAS_URL` | O `.env` não está na pasta do script ou está com nome errado. |
| `CERTIFICATE_VERIFY_FAILED` | Rede com proxy corporativo. Instale `truststore` no venv: `.\.venv\Scripts\python.exe -m pip install truststore`. |

## Segurança
- **Nunca** coloque o token no código, em mensagens, prints ou commits.
- Para revogar: **Conta > Configurações > Integrações aprovadas**, abra o token e clique em **Excluir**.
- Se o token vazar, revogue na hora e gere outro.
