from fastapi import FastAPI
from fastapi import status,HTTPException
from app.database import SessionLocal,Base,engine
from sqlalchemy.exc import IntegrityError
from app import models, schemas
from typing import List
import collections
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
app = FastAPI()
Base.metadata.create_all(engine)
db = SessionLocal()

@app.get("/books",response_model=List[schemas.BookResponseSchema],status_code=status.HTTP_200_OK)
def get_books():
    """
    get_books function searches and returns all the available books in the catalogue

    :return: list of books
    """
    logger.info("Getting all the books")
    books=db.query(models.Book).all()
    return books

@app.get("/books/{id}",response_model=schemas.BookResponseSchema,status_code=status.HTTP_200_OK)
def get_book_by_id(id: int):
    """
    get_book_by_id function searches and returns the book with the provided id

    :param id: book id 
    :return: book  with BookResponseSchema schema
    """
    logger.info(f"Getting book {id}")
    book=db.query(models.Book).filter(models.Book.id==id).first()
    if book is None:
        logger.error(f"Book id not found in the catalog")
        raise HTTPException(status_code=400,detail=f"Book id not found in the catalog")
    return book

@app.post("/books",response_model=schemas.BookResponseSchema,status_code=status.HTTP_201_CREATED)
def create_book(book:schemas.BookBaseSchema):
    """
    create_book function adds a new book with the provided attributes to the catalogue

    :param book: book with the BookBaseSchema schema
    :return: book with BookResponseSchema schema
    """
    logger.info(f"Creating book: {book}")
    try:
        new_book=models.Book(
            title=book.title,
            number_of_pages=book.number_of_pages,
            author=book.author,
            isbn=book.isbn,
            number_of_copies=book.number_of_copies,
            available_copies=book.available_copies
        )
        db.add(new_book)
        db.commit()
        logger.info(f"New book succesfully created. Title: {new_book.title}, number of pages: {new_book.number_of_pages}, author: {new_book.author}, isbn: {new_book.isbn}, number of copies: {new_book.number_of_copies}, available copies: {new_book.available_copies}")
        return new_book
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Book already exists")
        raise HTTPException(status_code=400,detail="Book already exists")

@app.post("/reserve",status_code=status.HTTP_200_OK)
def reserve_book(books:List[int]):
    """
    reserve_book function reserves available books from a given list provided by parameter

    :param books: a list of book ids to reserve
    """
    logger.info(f"Reserving books: {books}")
    book_collection = collections.Counter(books)
    books = db.query(models.Book).filter(models.Book.id.in_(list(book_collection.keys()))).with_for_update().all()
    if len(books) is not len(book_collection):
        db.rollback()
        logger.error(f"Book id not found in the catalog")
        raise HTTPException(status_code=400,detail=f"Book id not found in the catalog")
    for row in books:
        if row.available_copies<book_collection[row.id]:
            db.rollback()
            logger.error(f"There is no enough copies of the book with id {row.id} to reserve")
            raise HTTPException(status_code=400,detail=f"There is no enough copies of the book with id {row.id} to reserve")
        else:
            row.available_copies=row.available_copies-book_collection[row.id]
    db.commit()
    logger.info("Book/s succesfully reserved")