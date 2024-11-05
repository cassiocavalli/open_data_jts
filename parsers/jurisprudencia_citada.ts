import { AcordaoIndex } from './acordao_index';

export function parseJurisprudenciaCitada(jurisprudencia: string, index?: AcordaoIndex) {
  const resultado: any = { categorias: [] };
  
  if (!jurisprudencia) {
    return resultado;
  }

  try {
    let categoriaAtual: any = null;
    let acordaosAtuais: any[] = [];
    let tribunalAtual: string | null = null;

    const linhas = jurisprudencia.split('\n')
      .map(l => l.trim())
      .filter(l => l);

    for (const linha of linhas) {
      // Processa categoria
      if (linha.startsWith('(')) {
        if (categoriaAtual && acordaosAtuais.length) {
          categoriaAtual.acordaosCitados = acordaosAtuais;
          resultado.categorias.push(categoriaAtual);
          acordaosAtuais = [];
        }

        const match = linha.match(/^\((.*?)\)$/);
        if (match) {
          const categorias = match[1].split('-').map(c => c.trim());
          categoriaAtual = {
            categoriaPrincipal: categorias[0],
            subcategorias: categorias.slice(1)
          };
        }
      }
      // Processa citação
      else {
        const matchTribunal = linha.match(/^(STJ|STF)\s*-\s*/);
        if (matchTribunal) {
          tribunalAtual = matchTribunal[1];
          const restoLinha = linha.slice(matchTribunal[0].length).trim();

          const citacoes = restoLinha.split(/,\s*(?=<<|STJ|STF|REPERCUSSÃO|SÚMULA|TEMA)/);
          
          for (const citacao of citacoes) {
            if (!citacao.trim()) continue;

            const matchPadrao = citacao.match(/<<([^>]+)>>-(\w+)/);
            if (matchPadrao) {
              const [_, recursoCompleto, estado] = matchPadrao;
              const partes = recursoCompleto.split(/\s+/);
              const numero = partes[partes.length - 1];
              const tipo = partes.slice(0, -1).join(' ') || partes[0];

              const acordao: any = {
                tribunal: tribunalAtual,
                tipo,
                numero,
                estado
              };

              // Procura ID no índice
              if (index && tribunalAtual === "STJ") {
                const id = index.getId(tipo, numero);
                if (id) {
                  acordao.id = id;
                }
              }

              acordaosAtuais.push(acordao);
            }
          }
        }
      }
    }

    // Adiciona última categoria
    if (categoriaAtual && acordaosAtuais.length) {
      categoriaAtual.acordaosCitados = acordaosAtuais;
      resultado.categorias.push(categoriaAtual);
    }

  } catch (e) {
    console.error("Erro ao processar jurisprudência citada:", e);
  }

  return resultado;
}