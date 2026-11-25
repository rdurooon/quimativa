# Migração e compatibilidade — Qual molécula pertence à função

## Formatos aceitos

O formato atual contém exatamente quatro `cards`. Cada carta tem `id` e
exatamente um conteúdo: `content` (texto) ou `asset_id` (imagem). `supplementary_text`
é opcional e `correct_card_id` deve identificar uma das quatro cartas.
`target_function` é opcional para compatibilidade; novas questões devem
informar a função no enunciado.

O schema também converte na validação de entrada a forma antiga conhecida:

```json
{
  "target_function": "Amina",
  "molecules": [
    {"id": "M1", "asset_id": "asset-1"},
    {"id": "M2", "asset_id": "asset-2"},
    {"id": "M3", "asset_id": "asset-3"},
    {"id": "M4", "asset_id": "asset-4"}
  ],
  "correct_molecule_id": "M2"
}
```

Ela é mapeada para `cards` e `correct_card_id`. IDs, referências a assets,
textos complementares e demais campos são mantidos; campos desconhecidos ou
inválidos fazem a validação falhar em vez de serem descartados.
Essa conversão de entrada não reescreve por si só o JSON já armazenado.

## Migração persistente dos registros existentes

`backend/questoes/migracoes_payloads.py` implementa uma migração de dados
versionada, separada do histórico estrutural Alembic. A inicialização normal
(`backend/database/inicializacao.py`) executa a migração depois de aplicar as
migrações estruturais.

O migrador:

1. Examina somente questões do minijogo `function_molecule`.
2. Valida o conteúdo com o schema atual e confere que assets referenciados
   existem no banco e mantêm seus vínculos `question_assets`.
3. Persiste o formato novo apenas quando a validação e as relações permitem a
   conversão sem perda.
4. Mantém intactos payloads inválidos, cartas em quantidade diferente de
   quatro, IDs/gabaritos inconsistentes, campos desconhecidos e assets ou
   vínculos ausentes.
5. Salva contagens e motivos por ID em `app_metadata`, junto com as alterações,
   na mesma transação. Não altera assets nem suas relações.

Quando existem questões desse minijogo num banco persistente, a inicialização
cria primeiro uma cópia de segurança SQLite. O registro em `app_metadata` torna
a rotina idempotente: inicializações seguintes não convertem nem alteram
novamente os dados. Problemas individuais são registrados como avisos no log;
não impedem a abertura do restante do banco. O relatório persistido é a fonte
para identificar os registros que não foram convertidos.

## Compatibilidade de leitura e edição

Payloads antigos não convertidos continuam no banco sem serem apagados. Ao
ler/editar, o serviço tenta representá-los pelo schema atual. Se não for seguro
fazê-lo, retorna o erro controlado `payload_incompativel`, com explicação e
detalhes de validação; o payload original permanece intacto. A bridge traduz
esse erro no envelope padrão, sem produzir um objeto aparentemente válido. A
leitura também falha de forma controlada se uma carta referenciar um asset sem
relação persistida em `question_assets`.

Um payload legado conversível mas ainda não migrado pode ser lido na forma
normalizada pelo schema. Uma edição conserva `target_function` antigo quando o
formulário não o envia, para evitar perda de informação.

## Testes

`backend/tests/test_migracoes_payloads.py` cobre conversão com preservação de
IDs, assets, texto complementar e gabarito; dados inválidos preservados e
reportados; idempotência; preservação de vínculos; isolamento dos demais
minijogos; e rollback da transação. `backend/tests/test_servico_questoes.py`
cobre a resposta controlada na leitura/edição de payload não representável e
a preservação do conteúdo original.

O migrador recebe uma sessão SQLAlchemy e não faz `commit`: a inicialização
controla a transação. Os testes de migração devem usar banco temporário ou cópia,
nunca o banco original do usuário.
