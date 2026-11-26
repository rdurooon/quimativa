import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('./desktop', () => ({ callDesktop: vi.fn() }));

import { callDesktop } from './desktop';
import { criarPacote, ErroBridge, errosPorCampo, listarPacotes } from './questoes';

describe('serviço de questões', () => {
  beforeEach(() => {
    callDesktop.mockReset();
  });

  it('devolve apenas os dados quando a bridge responde ok', async () => {
    callDesktop.mockResolvedValue({ ok: true, dados: [{ id: 'base' }] });
    await expect(listarPacotes()).resolves.toEqual([{ id: 'base' }]);
    expect(callDesktop).toHaveBeenCalledWith('pacotes_listar');
  });

  it('envia o nome do pacote no formato do contrato', async () => {
    callDesktop.mockResolvedValue({ ok: true, dados: { id: 'x' } });
    await criarPacote('Revisão');
    expect(callDesktop).toHaveBeenCalledWith('pacotes_criar', { name: 'Revisão' });
  });

  it('lança ErroBridge com código e detalhes quando ok é false', async () => {
    callDesktop.mockResolvedValue({
      ok: false,
      erro: {
        codigo: 'dados_invalidos',
        mensagem: 'Dados inválidos',
        detalhes: [{ campo: 'name', mensagem: 'Já existe um pacote com esse nome' }],
      },
    });
    const erro = await criarPacote('Revisão').catch((e) => e);
    expect(erro).toBeInstanceOf(ErroBridge);
    expect(erro.codigo).toBe('dados_invalidos');
    expect(errosPorCampo(erro)).toEqual({ name: 'Já existe um pacote com esse nome' });
  });

  it('converte falha da ponte em ErroBridge', async () => {
    callDesktop.mockRejectedValue(new Error('O PyWebView não inicializou no tempo esperado.'));
    const erro = await listarPacotes().catch((e) => e);
    expect(erro).toBeInstanceOf(ErroBridge);
    expect(erro.codigo).toBe('bridge_indisponivel');
  });
});