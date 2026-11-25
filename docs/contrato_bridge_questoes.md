# Contrato da bridge — Banco de questões

Comunicação Vue ↔ Python pela API bridge do PyWebView (`window.pywebview.api`).
Implementação: `backend/api/questoes.py`. Regras de negócio: `backend/questoes/servico.py`.

## Envelope de resposta

Toda função devolve uma `Promise` com:

```js
// sucesso
{ ok: true, dados: ... }
// erro
{ ok: false, erro: { codigo: 'dados_invalidos', mensagem: 'Dados inválidos',
                     detalhes: [{ campo: 'payload.alternatives', mensagem: 'Precisa ter pelo menos 4 item(ns)' }] } }
```

| `codigo` | Quando acontece |
|---|---|
| `dados_invalidos` | Algum campo está errado. `detalhes` indica o campo (ex.: `payload.alternatives.2.label`) e a mensagem em português. |
| `nao_encontrado` | Questão, pacote ou imagem não existe. |
| `nao_permitido` | Operação proibida pela origem (editar/remover questão-base, remover pacote fixo, remover imagem em uso...). |
| `asset_indisponivel` | O registro do SVG existe, mas o arquivo não pode ser lido ou não é mais um SVG válido. |
| `payload_incompativel` | Questão legada não pode ser representada com segurança pelo formulário atual; o payload original permanece preservado. |
| `erro_interno` | Falha inesperada. Detalhes ficam só no log do aplicativo. |

Esperar o PyWebView ficar pronto antes da primeira chamada:

```js
window.addEventListener('pywebviewready', async () => {
  const r = await window.pywebview.api.questoes_metadados()
})
```

## Regras importantes para o frontend

1. **Permissões vêm do backend.** Use `permissions.edit` / `permissions.delete` de cada item para mostrar ou esconder botões. O backend recusa de qualquer forma.
2. **Imagens SVG sempre com `<img :src="asset.data_uri">`.** Nunca inserir o conteúdo do SVG na página (`v-html`).
3. **A tela não decide se a resposta está certa.** As funções abaixo são da tela de **gestão** (trazem o gabarito). A versão para partida, sem gabarito, virá no módulo de jogo.

## Objeto "questão"

```js
{
  id: '5b0e7c52-…', minigame_type: 'identification', minigame_name: 'Identificação de função orgânica',
  difficulty: 1, difficulty_name: 'Fácil',
  source_type: 'base' | 'local' | 'remote',
  statement: 'Qual função…', explanation: 'texto' | null,
  tags: ['Álcool'], status: null,
  source: { name, reference, license, notes } | null,
  package: { id, name } | null,
  preview_asset: { id, name } | null,    // listagem; sem Data URI
  created_at: '2026-11-24T23:10:00', updated_at: '…',
  permissions: { edit: false, delete: false },
  // somente em questoes_obter / criar / atualizar:
  payload: { … },                       // formato do minijogo (ver backend/questoes/schemas/)
  assets: { etanol: { id, name, source_type, asset_type, checksum, created_at, data_uri } }
}
```

Questões-base importadas são imutáveis. Criar uma questão manualmente com
`package_id: 'base'` associa-a ao pacote fixo e promove sua origem para `base`,
aplicando também as permissões de questão-base. Pacotes locais preservam a
origem `local`; removê-los desassocia suas questões sem removê-las nem alterar
payloads, assets ou fontes.

## Funções — questões e pacotes

| Função | Parâmetros | Retorno (`dados`) | Erros |
|---|---|---|---|
| `questoes_metadados()` | — | `{ minigames: [{value, name}], difficulties: [{value, name}], source_types: [{value, name, can_create, edit, delete}] }` | — |
| `questoes_listar(filtros?)` | objeto opcional (abaixo) | `{ items: [questão sem payload/assets], total, limite, deslocamento }` | `dados_invalidos` |
| `questoes_obter(id)` | `id: string` | questão completa | `nao_encontrado`, `asset_indisponivel`, `payload_incompativel` |
| `questoes_criar(dados)` | objeto "dados da questão" | questão completa (origem `local`, ou `base` ao escolher o pacote fixo) | `dados_invalidos`, `nao_encontrado`, `asset_indisponivel` |
| `questoes_atualizar(id, dados)` | `id: string`, dados completos (substitui tudo) | questão completa | `nao_encontrado`, `nao_permitido` (base/remota), `dados_invalidos`, `asset_indisponivel`, `payload_incompativel` |
| `questoes_remover(id)` | `id: string` | `{ id }` | `nao_encontrado`, `nao_permitido` (base) |
| `pacotes_listar()` | — | lista `{ id, name, kind, question_count, permissions }` | — |
| `pacotes_criar(dados)` | `{ name }` | pacote local com contagem zero | `dados_invalidos` (nome inválido/duplicado) |
| `pacotes_remover(id)` | `id: string` | `{ id }` | `nao_encontrado`, `nao_permitido` (pacote fixo) |

O pacote fixo usa `id: 'base'`, `kind: 'base'` e
`permissions.delete: false`; os pacotes do usuário têm `kind: 'local'` e
`permissions.delete: true`. A lista retorna primeiro o pacote fixo e depois os
locais por nome normalizado. Não há edição/renomeação de pacote na bridge.

**Filtros** (todos opcionais): `minigame_type`, `difficulty` (1–3), `source_type`, `tag` (ignora maiúsculas), `busca` (trecho do enunciado), `limite` (1–200, padrão 50), `deslocamento` (padrão 0). Ordem: mais recentes primeiro.

**Dados da questão** (criar/atualizar):

```js
{
  minigame_type: 'identification',     // obrigatório
  difficulty: 2,                       // obrigatório: 1, 2 ou 3
  statement: 'Qual função…',           // obrigatório
  payload: { … },                      // obrigatório, formato do minijogo
  package_id: 'id-do-pacote' | null,  // opcional; omitido equivale a Nenhum
  explanation: '…',                    // opcional
  tags: ['Álcool'],                    // opcional, até 20, sem repetir
  source: { name: 'ENEM 2023', reference: '…', license: '…', notes: 'adaptações' }  // opcional
}
```

O backend confere ainda se cada imagem citada no payload existe e se a região destacada (`highlight.region_id`) é um `id` existente dentro do SVG.

### Formatos específicos dos minijogos

- **Identificação:** `molecule_asset_id`, `highlight.region_id`, quatro
  `alternatives` e `correct_alternative_id`.
- **Encontre a diferença:** exatamente dois `molecules` (`id`, `asset_id`) e
  `correct_molecule_id`. `criterion` é opcional para payloads antigos; novos
  formulários usam `statement` como enunciado/critério.
- **Associação de cartas:** quatro `cards`; cada uma contém exatamente um
  `content` ou `asset_id`, e pode conter `supplementary_text`. `correct_pair`
  contém dois IDs diferentes.
- **Análise molecular:** mesmo formato validado de Identificação.
- **Qual molécula pertence à função:** quatro `cards`; cada carta tem `id` e
  exatamente um entre `content` (texto) ou `asset_id` (imagem), além de
  `supplementary_text` opcional. `correct_card_id` identifica exatamente uma
  carta. Payloads legados com `molecules` são convertidos quando representáveis;
  o campo legado `target_function` é preservado quando presente, mas a nova
  questão usa o enunciado para informar a função. A conversão persistente dos
  registros legados é executada uma vez na inicialização; ver
  [migração e compatibilidade](MIGRACAO_PAYLOADS_QUAL_MOLECULA.md).
- **Ordem das funções:** quatro `molecules` (`id`, `asset_id`) exclusivamente
  visuais e `correct_order`, uma lista ordenada com cada ID exatamente uma vez.
  Essa lista é a sequência correta definida pela ordem de marcação do criador;
  o backend a valida e preserva como recebida. Não existe `requested_order`
  nem conteúdo textual nas opções. Exemplo:

  ```js
  {
    molecules: [
      { id: 'M1', asset_id: 'alcool' }, { id: 'M2', asset_id: 'ester' },
      { id: 'M3', asset_id: 'amida' }, { id: 'M4', asset_id: 'amina' },
    ],
    correct_order: ['M1', 'M4', 'M3', 'M2'],
  }
  ```

**Remover** é definitivo. Imagens locais que ficarem sem uso são apagadas junto; imagens da base nunca.

## Funções — imagens (SVG)

| Função | Parâmetros | Retorno (`dados`) | Erros |
|---|---|---|---|
| `assets_importar_svg(conteudo, nome?)` | texto do arquivo `.svg`, nome amigável | imagem com `data_uri`, `usage_count`, `permissions` | `dados_invalidos` (SVG inválido/inseguro) |
| `assets_listar(origem?, com_conteudo?)` | `'base'`/`'local'`/`'remote'`; `true` para incluir `data_uri` | lista de imagens | `dados_invalidos`, `asset_indisponivel` |
| `assets_obter(id)` | `id: string` | imagem com `data_uri` | `nao_encontrado`, `asset_indisponivel` |
| `assets_remover(id)` | `id: string` | `{ id }` | `nao_permitido` (base ou em uso) |

Enviar o mesmo SVG duas vezes devolve a imagem já existente (não duplica).
Questões e assets podem referenciar o mesmo SVG. Se o registro existir, mas o
arquivo estiver ausente ou inválido, a chamada falha com `asset_indisponivel`;
não retorna uma resposta de sucesso sem imagem.

## Exemplos

```js
const api = window.pywebview.api

// listar questões locais de identificação
const r = await api.questoes_listar({ source_type: 'local', minigame_type: 'identification' })
if (r.ok) questoes.value = r.dados.items

// importar SVG escolhido num <input type="file">
const texto = await arquivo.text()
const img = await api.assets_importar_svg(texto, arquivo.name.replace('.svg', ''))

// criar questão usando a imagem
const nova = await api.questoes_criar({
  minigame_type: 'identification', difficulty: 1, statement: 'Qual função está destacada?',
  payload: {
    molecule_asset_id: img.dados.id, highlight: { region_id: 'grupo-oh' },
    alternatives: [{ id: 'A', label: 'Álcool' }, { id: 'B', label: 'Cetona' },
                   { id: 'C', label: 'Éster' }, { id: 'D', label: 'Aldeído' }],
    correct_alternative_id: 'A',
  },
})
if (!nova.ok) mostrarErros(nova.erro.detalhes)   // [{ campo, mensagem }]
```
