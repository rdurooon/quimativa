import { describe, expect, it } from "vitest";
import { destacarRegiao } from "./svgDestaque";

const svg =
  '<svg xmlns="http://www.w3.org/2000/svg"><title>Ácido</title><g id="grupo-oh"><text>OH</text></g></svg>';
const dataUri = `data:image/svg+xml;base64,${btoa(String.fromCharCode(...new TextEncoder().encode(svg)))}`;

function conteudo(uri) {
  const bytes = Uint8Array.from(atob(uri.split(",")[1]), (c) =>
    c.charCodeAt(0),
  );
  return new TextDecoder().decode(bytes);
}

describe("destacarRegiao", () => {
  it("acrescenta o estilo de destaque para a região escolhida", () => {
    const resultado = conteudo(destacarRegiao(dataUri, "grupo-oh"));
    expect(resultado).toContain('[id="grupo-oh"]');
    expect(resultado).toContain('<g id="grupo-oh">');
    expect(resultado).toContain("Ácido");
  });

  it("sem região devolve a imagem original", () => {
    expect(destacarRegiao(dataUri, "")).toBe(dataUri);
  });
});
