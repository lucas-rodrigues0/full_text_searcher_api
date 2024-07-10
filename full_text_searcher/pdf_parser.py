import os
from os import environ as env
from dotenv import find_dotenv, load_dotenv

from collections import defaultdict
from PyPDF2 import PdfReader
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT
from sqlalchemy.exc import IntegrityError

from models import db_session, PdfPages


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class PdfParser:
    """Classe que analiza o PDF. Faz a indexação e insere o conteúdo no database."""

    index_dir = os.path.dirname(os.path.realpath(__file__)) + "/index_directory"
    pdf_file_path = os.path.dirname(os.path.realpath(__file__)) + "/resources/CF.pdf"
    idx_first_page = int(env.get("CF_SUMARIO_FIRST_PAGE"))
    idx_last_page = int(env.get("CF_SUMARIO_LAST_PAGE"))
    cf_last_page = int(env.get("CF_LAST_PAGE"))
    titulo_idx = defaultdict(list)
    capitulo_idx = defaultdict(list)

    def __init__(self) -> None:
        self._set_index_for_pages()

    def _set_index_for_pages(self):
        """Analiza o sumário da Constituição Federal para pegar as referências
        de Títulos e Capítulos e suas páginas utilizado na indexação."""
        titulo = ""
        capitulo = ""
        cont_linha = False
        divisao_value = ""
        divisao_type = defaultdict(list)

        with open(self.pdf_file_path, "rb") as file:
            reader = PdfReader(file)
            # Lê somente as páginas do Sumário
            for page in reader.pages[self.idx_first_page : self.idx_last_page]:

                page_content = page.extract_text()
                lines = page_content.splitlines()

                for line in lines:
                    words = line.split()
                    first_word = words[0]
                    if len(words) > 1:
                        second_word = words[1]
                        last_word = words[-1]
                    else:
                        second_word = ""
                        last_word = ""

                    if cont_linha:
                        divisao_type[int(last_word)].append(divisao_value)
                        cont_linha = False

                    match first_word:
                        case "Título":
                            titulo = "Título " + second_word
                            if last_word.isnumeric():
                                self.titulo_idx[int(last_word)].append(titulo)
                            else:
                                cont_linha = True
                                divisao_value = titulo
                                divisao_type = self.titulo_idx
                        case "Capítulo":
                            capitulo = "Capítulo " + second_word
                            if last_word.isnumeric():
                                self.capitulo_idx[int(last_word)].append(capitulo)
                            else:
                                cont_linha = True
                                divisao_value = capitulo
                                divisao_type = self.capitulo_idx
                        case _:
                            continue

            self.titulo_idx[self.cf_last_page] = [""]
            self.capitulo_idx[self.cf_last_page] = []
        print("Parser initialized!")

    def index_pdf_by_pages(self):
        """Extração das páginas do PDF da Constituição Federal, e a indexação do
        conteúdo de cada página. Cria um diretório para esse index, ou utiliza um
        já existente. Insere o conteúdo de cada página no database.
        """
        print("Initialize indexation...")

        # Schema do índice
        schema = Schema(
            path=ID(stored=True),
            content=TEXT(stored=True),
            titulo=TEXT(stored=True),
            capitulo=TEXT(stored=True),
        )

        # Criação do diretório de índice ou abertura se já existir
        print("Create/update index directory...")
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir, exist_ok=True)
            ix = create_in(self.index_dir, schema)
            print("directory created!")
        else:
            ix = open_dir(self.index_dir)
            print("directory opened!")

        # Abre conexão com a base de dados para inserir o conteudo das pagina
        db = db_session()

        # Criação ou obtenção do escritor do índice
        writer = ix.writer()

        # Extrair texto do PDF
        print("Extracting PDF pages...")
        titulo = ""
        capitulo = []
        extracted_pages = 0

        with open(self.pdf_file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                page_num = reader.get_page_number(page)
                page_content = page.extract_text()
                pdf_pag_num = page_num + 1

                if page_num in self.titulo_idx:
                    titulo = self.titulo_idx[page_num][0]
                if page_num in self.capitulo_idx:
                    capitulo = self.capitulo_idx[page_num]

                if page_content:
                    titulo_num = titulo
                    capitulo_num = capitulo
                else:
                    titulo_num = ""
                    capitulo_num = []

                pdf_page = PdfPages(
                    page_num=int(pdf_pag_num),
                    page_content=page_content,
                    titulo_num=titulo_num,
                    capitulo_num=capitulo_num,
                )

                db.add(pdf_page)
                writer.add_document(
                    path=str(pdf_pag_num),
                    content=page_content,
                    titulo=titulo_num,
                    capitulo=capitulo_num,
                )
                extracted_pages += 1

        print(f"{extracted_pages} pages extracted!")

        # Finalizar e otimizar o índice e a inserção na base
        writer.commit(optimize=True)
        print("Index committed")
        try:
            db.commit()
            print("Pages commited to database")
        except IntegrityError as e:
            print("Pages already inserted into database")
        except Exception as e:
            print(f"error: {e}")
        finally:
            db.close()
