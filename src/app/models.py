from .database import Base
from sqlalchemy import  Column, Integer, String


class Book(Base):
    """Book declaring model for SQLAlchemy (PostgreSQL)

    Attributes:
        id: An integer incremental unique identifier of the book provided by the database.
        title: A string with the book title.
        number_of_pages: An integer count of the number of pages of the book.
        author: A string with the name of the book author.
        isbn: 13 digits string with the International Standard Book Number (ISBN), a unique identifier of the book.
        number_of_copies: An integer count of the total number of copies of the book.
        available_copies: An integer count of the number of copies of the book available for reservation.
    """
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    number_of_pages = Column(Integer, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String(13), nullable=False, unique=True)
    number_of_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)

