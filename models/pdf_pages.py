from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from typing import List

from models import Base


class PdfPages(Base):
    __tablename__ = "pdf_pages"

    page_num = Column(Integer, primary_key=True)
    titulo_num = Column(String(15), nullable=True)
    capitulo_num = Column(ARRAY(String), nullable=True)
    page_content = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def __init__(
        self,
        page_num: int,
        page_content: str,
        titulo_num: str = None,
        capitulo_num: List[str] = None,
    ):
        self.page_num = page_num
        self.page_content = page_content
        if titulo_num:
            self.titulo_num = titulo_num
        if capitulo_num:
            self.capitulo_num = capitulo_num
