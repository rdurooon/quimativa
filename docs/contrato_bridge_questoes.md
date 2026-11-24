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
| `nao_encontrado` | Questão ou imagem não existe. |
| `nao_permitido` | Operação proibida pela origem (editar questão-base, remover imagem em uso...). |
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
  created_at: '2026-11-24T23:10:00', updated_at: '…',
  permissions: { edit: false, delete: false },
  // somente em questoes_obter / criar / atualizar:
  payload: { … },                       // formato do minijogo (ver backend/questoes/schemas/)
  assets: { etanol: { id, name, source_type, asset_type, checksum, created_at, data_uri } }
}
```

## Funções — questões

| Função | Parâmetros | Retorno (`dados`) | Erros |
|---|---|---|---|
| `questoes_metadados()` | — | `{ minigames: [{value, name}], difficulties: [{value, name}], source_types: [{value, name, can_create, edit, delete}] }` | — |
| `questoes_listar(filtros?)` | objeto opcional (abaixo) | `{ items: [questão sem payload/assets], total, limite, deslocamento }` | `dados_invalidos` |
| `questoes_obter(id)` | `id: string` | questão completa | `nao_encontrado` |
| `questoes_criar(dados)` | objeto "dados da questão" | questão completa (origem `local`) | `dados_invalidos` |
| `questoes_atualizar(id, dados)` | `id: string`, dados completos (substitui tudo) | questão completa | `nao_encontrado`, `nao_permitido` (base/remota), `dados_invalidos` |
| `questoes_remover(id)` | `id: string` | `{ id }` | `nao_encontrado`, `nao_permitido` (base) |

**Filtros** (todos opcionais): `minigame_type`, `difficulty` (1–3), `source_type`, `tag` (ignora maiúsculas), `busca` (trecho do enunciado), `limite` (1–200, padrão 50), `deslocamento` (padrão 0). Ordem: mais recentes primeiro.

**Dados da questão** (criar/atualizar):

```js
{
  minigame_type: 'identification',     // obrigatório
  difficulty: 2,                       // obrigatório: 1, 2 ou 3
  statement: 'Qual função…',           // obrigatório
  payload: { … },                      // obrigatório, formato do minijogo
  explanation: '…',                    // opcional
  tags: ['Álcool'],                    // opcional, até 20, sem repetir
  source: { name: 'ENEM 2023', reference: '…', license: '…', notes: 'adaptações' }  // opcional
}
```

O backend confere ainda se cada imagem citada no payload existe e se a região destacada (`highlight.region_id`) é um `id` existente dentro do SVG.

**Remover** é definitivo. Imagens locais que ficarem sem uso são apagadas junto; imagens da base nunca.

## Funções — imagens (SVG)

| Função | Parâmetros | Retorno (`dados`) | Erros |
|---|---|---|---|
| `assets_importar_svg(conteudo, nome?)` | texto do arquivo `.svg`, nome amigável | imagem com `data_uri`, `usage_count`, `permissions` | `dados_invalidos` (SVG inválido/inseguro) |
| `assets_listar(origem?, com_conteudo?)` | `'base'`/`'local'`/`'remote'`; `true` para incluir `data_uri` | lista de imagens | `dados_invalidos` |
| `assets_obter(id)` | `id: string` | imagem com `data_uri` | `nao_encontrado` |
| `assets_remover(id)` | `id: string` | `{ id }` | `nao_permitido` (base ou em uso) |

Enviar o mesmo SVG duas vezes devolve a imagem já existente (não duplica).

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
