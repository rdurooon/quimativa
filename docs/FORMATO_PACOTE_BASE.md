# Recebimento do pacote oficial Questões-base

O conteúdo pedagógico oficial será recebido separadamente. Este documento
descreve o formato técnico esperado; não contém questões nem SVGs oficiais.
`docs/pacote_base_exemplo/` é somente uma fixture de desenvolvimento/teste.

## Caminhos de distribuição

Os caminhos definidos em `backend/config.py` são:

- Manifesto: `backend/questoes/dados/pacote_base.json`
- Raiz dos SVGs: `backend/questoes/assets/base/`

O campo `file` de cada asset é relativo à raiz de SVGs. Por exemplo,
`alcoois/etanol.svg` corresponde a
`backend/questoes/assets/base/alcoois/etanol.svg`. Organizar os arquivos em
subpastas por grupo químico é permitido; não usar caminhos absolutos ou
`..`.

O DOCX/PDF de Pedro serve para revisão editorial. O importador não lê DOCX ou
PDF: após revisão, o conteúdo aprovado deve ser transcrito para o manifesto
JSON e cada referência de imagem deve apontar para um `id` de asset declarado.

## Formato do manifesto

O schema é `PacoteQuestoesBase`, em `backend/questoes/schemas/pacote_base.py`.
O objeto raiz contém:

```json
{
  "version": 1,
  "assets": [
    {
      "id": "etanol",
      "file": "alcoois/etanol.svg",
      "name": "Etanol"
    }
  ],
  "questions": [
    {
      "id": "UUID fixo da questão",
      "minigame_type": "identification",
      "difficulty": 1,
      "statement": "Enunciado aprovado",
      "payload": {
        "molecule_asset_id": "etanol",
        "highlight": {"region_id": "grupo-oh"},
        "alternatives": [
          {"id": "A", "label": "Álcool"},
          {"id": "B", "label": "Cetona"},
          {"id": "C", "label": "Éster"},
          {"id": "D", "label": "Aldeído"}
        ],
        "correct_alternative_id": "A"
      },
      "explanation": "Explicação opcional",
      "tags": ["Álcool"],
      "source": {
        "name": "Referência aprovada",
        "reference": "Identificação bibliográfica ou URL",
        "license": null,
        "notes": null
      }
    }
  ]
}
```

Regras do schema:

- `version` é inteiro maior ou igual a 1.
- `assets` declara `id`, caminho relativo `file` e `name` opcional. IDs e
  caminhos não podem se repetir.
- `questions` declara ID UUID estável, tipo de minijogo, dificuldade,
  enunciado e payload válidos para os schemas atuais. IDs de questão não podem
  se repetir.
- `explanation`, `tags` e `source` são opcionais conforme `DadosQuestao`.
- Cada payload referencia assets pelos IDs declarados em `assets`, não pelo
  nome do arquivo. O caminho físico é resolvido pelo campo `file`.
- Questões importadas recebem a associação ao pacote fixo no backend; não
  incluir `package_id` no manifesto.
- A validação verifica que todos os assets referenciados estão declarados,
  que cada SVG existe e é seguro, e que as regiões de destaque existem no SVG.
- Questões devem respeitar o contrato atual dos seis minijogos. Em particular,
  Ordem das funções usa `molecules` e `correct_order`; não usa
  `requested_order`.

O importador é `backend/questoes/importador.py::importar_pacote_base`. Ele
valida o manifesto e os arquivos antes de persistir, opera transacionalmente e
não remove questões que deixaram de constar em uma nova versão.

## Manifesto ausente

Na ausência de `pacote_base.json`, o importador retorna
`ResultadoImportacao(status='sem_pacote')` e registra uma mensagem informativa.
O pacote fixo na base SQLite continua existindo; a falta temporária do
conteúdo oficial não impede a inicialização do aplicativo.

Não criar conteúdo substituto nem mover o caminho configurado. Depois que os
arquivos oficiais forem recebidos e revisados, validar o JSON e os SVGs com o
importador antes de distribuir a nova versão.
