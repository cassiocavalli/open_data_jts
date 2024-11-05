import { AcordaoIndex } from './acordao_index';

export function parseAcordaosSimilares(acordaos: string[], index?: AcordaoIndex) {
  const resultado: any = {};

  if (!acordaos?.length) {
    return resultado;
  }

  acordaos.forEach((acordao, idx) => {
    try {
      const linhas = acordao.split('\n')
        .map(l => l.trim())
        .filter(l => l);

      if (!linhas.length) return;

      const primeiraLinha = linhas[0].replace(/\s+/g, ' ');

      const matchRegistro = primeiraLinha.match(/(\d{4}\/\d{7}-\d)/);
      if (!matchRegistro) return;

      const registro = matchRegistro[1];
      const textoAntes = primeiraLinha.slice(0, matchRegistro.index).trim();

      const partes = textoAntes.split(/\s+/);
      if (partes.length < 3) return;

      const estado = partes[partes.length - 1];
      const numero = partes[partes.length - 2];
      const tipo = partes.slice(0, -2).join(' ');

      const acordaoDict: any = {
        tribunal: 'STJ',
        tipo: tipo.trim(),
        numero,
        estado,
        registro
      };

      // Procura ID no índice
      if (index) {
        const id = index.getId(tipo.trim(), numero);
        if (id) {
          acordaoDict.id = id;
        }
      }

      resultado[`acordaoSimilar${idx + 1}`] = acordaoDict;

    } catch (e) {
      console.error(`Erro ao processar acórdão similar ${idx + 1}:`, e);
    }
  });

  return resultado;
}