from os import environ as env
from dotenv import find_dotenv, load_dotenv

from api import api
from models import inspector, create_tables
from full_text_searcher import PdfParser


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


if __name__ == "__main__":
    if not inspector.get_table_names():
        create_tables()

    parser = PdfParser()

    parser.index_pdf_by_pages()

    api.run(
        host="0.0.0.0", port=env.get("API_PORT", 4000), debug=env.get("DEBUG", False)
    )
