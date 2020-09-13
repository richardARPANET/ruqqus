from flask import render_template
from sqlalchemy import *
from sqlalchemy.orm import relationship

from ruqqus.__main__ import Base

class BoardCategories(Base):

    __tablename__ = "board_categories"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    board_id = Column(Integer, ForeignKey("boards.id"))
    created_utc = Column(Integer)
    category = relationship("Categories", lazy="dynamic")
    def __repr__(self):
        return f"<BoardCategories(id={self.id}, board_id={self.board_id})>"

    @property
    def json(self):
        return {'id': self.id,
                'category_id': self.category_id,
                'board_id': self.board_id,
                'created_utc': self.created_utc,
                'name':self.category.name,
                'description': self.category.description
                ,}


class Categories(Base):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    description = Column(String(256))
    created_utc = Column(Integer)

    def __repr__(self):
        return f"<Categories(id={self.id})>"

    @property
    def json(self):
        return {'id': self.id,
                'type': self.name,
                'description': self.description,
                'created_utc': self.created_utc
                }