import { markRaw } from "vue";
import FormIdentificacao from "./FormIdentificacao.vue";
import * as identificacao from "./identificacao";
import FormEncontreDiferenca from "./FormEncontreDiferenca.vue";
import * as encontreDiferenca from "./encontreDiferenca";
import FormAssociacao from "./FormAssociacao.vue";
import * as associacao from "./associacao";
import FormMoleculaDaFuncao from "./FormMoleculaDaFuncao.vue";
import * as moleculaDaFuncao from "./moleculaDaFuncao";
import FormOrdemFuncoes from "./FormOrdemFuncoes.vue";
import * as ordemFuncoes from "./ordemFuncoes";

// minigame_type -> { componente, criarRascunho, validar, paraPayload, deQuestao }
export const FORMULARIOS = {
  identification: { componente: markRaw(FormIdentificacao), ...identificacao },
  molecular_analysis: {
    componente: markRaw(FormIdentificacao),
    ...identificacao,
  },
  find_difference: {
    componente: markRaw(FormEncontreDiferenca),
    ...encontreDiferenca,
  },
  card_association: { componente: markRaw(FormAssociacao), ...associacao },
  function_molecule: {
    componente: markRaw(FormMoleculaDaFuncao),
    ...moleculaDaFuncao,
  },
  function_order: { componente: markRaw(FormOrdemFuncoes), ...ordemFuncoes },
};
