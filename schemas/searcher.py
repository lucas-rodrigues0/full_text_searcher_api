from pydantic import BaseModel


class SearcherQuerySchema(BaseModel):
    """Define como a Query Parameter será representada no searcher"""

    query: str = "direito"


class SearcherResponseSchema(BaseModel):
    """Define como a resposta do searcher será representada"""

    hits: list
