from starlette.testclient import TestClient
from app.main import app
import json
import random
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
client = TestClient(app)

def test_get_books():
    logger.info('Testing function get_books()')
    response = client.get("/books")
    assert response.status_code == 200
    assert type(response.json()) == type([])

def test_get_book_by_id_incorrect_id():
    logger.info('Testing function get_book_by_id() with a non-existing id')
    id = 100000000
    response = client.get(f"/books/{id}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Book id not found in the catalog"

def test_get_book_by_id_negative_id():
    logger.info('Testing function get_book_by_id() with a negative id')
    id = -1
    response = client.get(f"/books/{id}")
    assert response.status_code == 422

def test_get_book_by_id():
    logger.info('Testing function get_book_by_id()')
    title = "Test book"
    number_of_pages = 500
    author = "Test author"
    isbn = str(random.randint(1000000000000,9999999999999))
    number_of_copies = 7
    available_copies = 6
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
    response_post = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    id = response_post.json()["id"]
    logger.info(f"New book created with id {id}")
    logger.info(f"Trying to get book with id {id}")
    response_get = client.get(f"/books/{id}")
    assert response_get.status_code == 200
    assert response_post.json()["id"] == response_get.json()["id"]
    assert response_post.json()["title"] == response_get.json()["title"]
    assert response_post.json()["number_of_pages"] == response_get.json()["number_of_pages"]
    assert response_post.json()["author"] == response_get.json()["author"]
    assert response_post.json()["isbn"] == response_get.json()["isbn"]
    assert response_post.json()["number_of_copies"] == response_get.json()["number_of_copies"]
    assert response_post.json()["available_copies"] == response_get.json()["available_copies"]

def test_create_book_already_exists():
    logger.info('Testing function create_book() with an already-existing book')
    title = "Test book"
    number_of_pages = 500
    author = "Test author"
    isbn = str(random.randint(1000000000000,9999999999999))
    number_of_copies = 7
    available_copies = 6
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
    response = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
    response = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Book already exists"

def test_create_book_missing_parameter():
    logger.info('Testing function create_book() with a missing parameter')
    title = "Test book"
    number_of_pages = 500
    author = "Test author"
    isbn = str(random.randint(1000000000000,9999999999999))
    number_of_copies = 7
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}")
    response = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
        })
    )
    assert response.status_code == 422

def test_create_book_incorrect_parameters():
    logger.info('Testing function create_book() with incorrect parameters')
    title = "Test book"
    number_of_pages = -500
    author = "Test author"
    isbn = str(12345678912345)
    number_of_copies = -7
    available_copies = -6
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}")
    response = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    assert response.status_code == 422

def test_create_book():
    logger.info('Testing function create_book()')
    title = "Test book"
    number_of_pages = 500
    author = "Test author"
    isbn = str(random.randint(1000000000000,9999999999999))
    number_of_copies = 7
    available_copies = 6
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
    response = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    id = response.json()["id"]
    assert response.status_code == 201
    assert type(id) is int
    assert response.json()["title"] == title
    assert response.json()["number_of_pages"] == number_of_pages
    assert response.json()["author"] == author
    assert response.json()["isbn"] == isbn
    assert response.json()["number_of_copies"] == number_of_copies
    assert response.json()["available_copies"] == available_copies

def test_reserve_book_no_copies():
    logger.info('Testing function reserve_book() with insufficient number of copies')
    title = "Test book"
    number_of_pages = 500
    author = "Test author"
    isbn = str(random.randint(1000000000000,9999999999999))
    number_of_copies = 7
    available_copies = 1
    logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
    response_create = client.post(
        "/books", content=json.dumps({
            "title": title,
            "number_of_pages": number_of_pages,
            "author": author,
            "isbn": isbn,
            "number_of_copies": number_of_copies,
            "available_copies": available_copies
        })
    )
    id = response_create.json()["id"]
    logger.info(f"New book created with id {id}")
    logger.info(f"Trying to reserve 2 copies of book {id}")
    response_reserve = client.post("/reserve", content=json.dumps([id,id]))
    assert response_reserve.status_code == 400
    assert response_reserve.json()["detail"] == f"There is no enough copies of the book with id {id} to reserve"

def test_reserve_book_incorrect_id():
    logger.info('Testing function reserve_book() with non-existing book')
    id = 100000000
    logger.info(f"Trying to reserve 1 copy of book {id}")
    response_reserve = client.post("/reserve", content=json.dumps([id]))
    assert response_reserve.status_code == 400
    assert response_reserve.json()["detail"] == "Book id not found in the catalog"

def test_reserve_book_negative_id():
    logger.info('Testing function reserve_book() with negative id')
    response_reserve = client.post("/reserve", content=json.dumps([-1]))
    assert response_reserve.status_code == 422

def test_reserve_book():
    logger.info('Testing function reserve_book()')
    ids = []
    for i in range(3):
        title = "Test book"
        number_of_pages = 500
        author = "Test author"
        isbn = str(random.randint(1000000000000,9999999999999))
        number_of_copies = 7
        available_copies = 5
        logger.info(f"Trying to create new book. Title: {title}, number of pages: {number_of_pages}, author: {author}, isbn: {isbn}, number of copies: {number_of_copies}, available copies: {available_copies}")
        response_create = client.post(
            "/books", content=json.dumps({
                "title": title,
                "number_of_pages": number_of_pages,
                "author": author,
                "isbn": isbn,
                "number_of_copies": number_of_copies,
                "available_copies": available_copies
            })
        )
        id = response_create.json()["id"]
        logger.info(f"New book created with id {id}")
        ids.append(id)
    books_to_reserve = [ids[0],ids[1],ids[0],ids[1],ids[2],ids[2]]
    logger.info(f"Trying to reserve {books_to_reserve}")
    response_reserve = client.post("/reserve", content=json.dumps(books_to_reserve))
    assert response_reserve.status_code == 200
    for id in ids:
        response_get = client.get(f"/books/{id}")
        assert response_get.json()["available_copies"] == 3



