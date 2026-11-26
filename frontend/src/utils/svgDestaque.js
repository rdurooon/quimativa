const COR_DESTAQUE = "#008e15";

function decodificar(dataUri) {
  const [cabecalho, corpo = ""] = dataUri.split(",", 2);
  if (!cabecalho.includes(";base64")) return decodeURIComponent(corpo);
  const bytes = Uint8Array.from(atob(corpo), (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function codificar(texto) {
  const bytes = new TextEncoder().encode(texto);
  let binario = "";
  bytes.forEach((b) => {
    binario += String.fromCharCode(b);
  });
  return `data:image/svg+xml;base64,${btoa(binario)}`;
}

/**
 * Devolve uma cópia da Data URI com a região `regionId` pintada de verde, para a prévia.
 * O SVG continua sendo exibido por <img>, nunca inserido na página.
 */
export function destacarRegiao(dataUri, regionId) {
  if (!dataUri || !regionId) return dataUri;
  const documento = new DOMParser().parseFromString(
    decodificar(dataUri),
    "image/svg+xml",
  );
  const svg = documento.documentElement;
  if (svg.nodeName !== "svg") return dataUri;

  const id = regionId.replace(/["\\]/g, "\\$&");
  const estilo = documento.createElementNS(
    "http://www.w3.org/2000/svg",
    "style",
  );
  estilo.textContent =
    `[id="${id}"], [id="${id}"] * { fill: ${COR_DESTAQUE} !important; ` +
    `stroke: ${COR_DESTAQUE} !important; font-weight: 700; }`;
  svg.appendChild(estilo);
  return codificar(new XMLSerializer().serializeToString(documento));
}
