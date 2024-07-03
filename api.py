from flask_openapi3 import OpenAPI, Info, Tag
from flask import request

from schemas import SearcherResponseSchema, ErrorSchema, SearcherQuerySchema
from full_text_searcher import query_full_text_searcher


info = Info(title="Searcher API", version="1.0.0")

api = OpenAPI(__name__, info=info)

searcher_tag = Tag(
    name="Searcher",
    description="Busca por termos existentes no conteúdo de PDF com técnica de full-text search",
)


@api.get("/", tags=[searcher_tag])
def home():
    return {"message": "You are in the Searcher API"}, 200


@api.get(
    "/searcher",
    tags=[searcher_tag],
    responses={"200": SearcherResponseSchema, "403": ErrorSchema},
)
def query_searcher(query: SearcherQuerySchema):
    """Faz um full-text search dos termos, em conteúdo do PDF indexado.
    Retorna os resultados contendo as páginas em que forma encontrados os termos,
    assim como uma amostragem do conteúdo, onde cada termos foi encontrado.
    """

    data = request.args
    query_param = data.get("query")
    results = query_full_text_searcher(query=query_param)

    return {"data": {"results": results, "total_count": len(results)}}, 200
