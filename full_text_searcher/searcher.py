import os
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, OrGroup, FuzzyTermPlugin
from whoosh import highlight


class CustomFormatter(highlight.Formatter):
    def format_token(self, text, token, replace=False):
        # Utiliza a função get_text para extrair o texto correspondente ao token (termos na busca)
        tokentext = highlight.get_text(text, token, replace)

        # retorna o texto da amostragem juntamente com o termo da busca dentro da tag htlm utilizada
        return "<strong class='highlight'>%s</strong>" % tokentext


def query_full_text_searcher(query):
    """Função para realizar a busca dos termos pelo index do arquivo PDF
    Retorna o número das páginas onde os termos foram encontrados, assim como uma amostragem
    do conteúdo próximo aos termos encontrados.
    Utiliza um formatador customizado para que a amostragem seja apresentada em um html.
    """
    # Caminho para o diretório de índice
    index_dir = os.path.dirname(os.path.realpath(__file__)) + "/index_directory"

    # abertura do diretório de índice
    ix = open_dir(index_dir)

    pages_result = {}

    # context manager para o objeto searcher ser fechado ao final da busca
    with ix.searcher() as searcher:
        og = OrGroup.factory(0.9)
        parser = QueryParser("content", ix.schema, group=og)
        parser.add_plugin(FuzzyTermPlugin())
        query = parser.parse(query)

        # configura opções para a apresentação dos resultados e das amostragens de conteúdo
        results = searcher.search(query, limit=20)
        results.fragmenter.maxchars = 300
        results.fragmenter.surround = 50

        # utiliza o formatador customizado para a amostragem de conteúdo
        custom_formatter = CustomFormatter()
        results.formatter = custom_formatter

        for hit in results:
            capitulo = ", ".join(hit["capitulo"])
            pages_result[hit["path"]] = {
                "_page_info": {
                    "Titulo": hit["titulo"],
                    "Capitulo": capitulo,
                },
                "content": hit.highlights("content"),
            }

    print(f"{len(pages_result)} Results hits")
    return pages_result
