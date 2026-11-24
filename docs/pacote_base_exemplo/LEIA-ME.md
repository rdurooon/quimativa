# Pacote de questões-base — exemplo

Modelo do arquivo que leva as questões oficiais (questões-base) para dentro do Quimativa.
Este exemplo tem **uma questão de cada minijogo** e é verificado automaticamente nos testes.

> Os SVGs deste exemplo são ilustrativos (fórmulas simplificadas), só para mostrar o formato.

## Onde ficam os arquivos no software

| Arquivo | Local |
|---|---|
| Pacote | `backend/questoes/dados/pacote_base.json` |
| SVGs | `backend/questoes/assets/base/` (os caminhos em `file` são relativos a esta pasta) |

O app importa o pacote ao abrir, **somente quando `version` é maior que a versão já instalada**.

## Regras

- `version`: número inteiro; aumente a cada atualização oficial do conteúdo.
- `assets`: cada SVG tem um `id` fixo (ex.: `etanol`) e pode ser usado em várias questões.
- `questions[].id`: **UUID fixo**, gerado uma única vez e nunca alterado:
  `python -c "import uuid; print(uuid.uuid4())"`
- `difficulty`: 1 = Fácil, 2 = Média, 3 = Difícil.
- `minigame_type`: `identification`, `find_difference`, `card_association`,
  `molecular_analysis`, `function_molecule`, `function_order`.
- `payload`: formato próprio de cada minijogo (ver exemplos no `pacote_base.json` e as
  explicações em `backend/questoes/schemas/`).
- `source` (opcional): fonte externa e, em `notes`, as adaptações feitas.

## Região destacada

Quando o minijogo destaca uma parte da molécula (`highlight.region_id`), essa parte precisa
estar dentro de um elemento do SVG com o mesmo `id`, por exemplo:

```xml
<g id="grupo-oh"> ... desenho do –OH ... </g>
```

O importador confere se o `id` existe; se não existir, o pacote é recusado inteiro.

## SVGs aceitos

Sem `<script>`, sem atributos `on...` (onclick, onload...), sem `<foreignObject>`, sem links
ou imagens externas, até 2 MB. SVGs exportados de editores de moléculas normalmente passam;
se algum for recusado, a mensagem diz o motivo.
