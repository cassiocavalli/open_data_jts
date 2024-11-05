import { AcordaoIndex } from './parsers/acordao_index';
import { parseJurisprudenciaCitada } from './parsers/jurisprudencia_citada';
import { parseAcordaosSimilares } from './parsers/acordaos_similares';
// ... outros imports

export function processAcordao(acordao: any, index: AcordaoIndex) {
  // ... outros processamentos

  // Processa jurisprudência citada
  if (acordao.jurisprudenciaCitada) {
    acordao.jurisprudenciaCitadaEstruturada = parseJurisprudenciaCitada(
      acordao.jurisprudenciaCitada,
      index
    );
  }

  // Processa acórdãos similares
  if (acordao.acordaosSimilares?.length) {
    acordao.acordaosSimilaresEstruturados = parseAcordaosSimilares(
      acordao.acordaosSimilares,
      index
    );
  }

  return acordao;
}

export async function processDirectory(inputPath: string, outputPath: string) {
  // Primeiro constrói o índice
  const index = new AcordaoIndex();
  await index.buildFromDirectory(inputPath);

  // ... resto do processamento passando o index
}