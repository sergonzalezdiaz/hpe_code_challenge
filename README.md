# Code challenge

## Frameworks and toolkits
For the development of the API of this code challenge I have decided to use:
- [FastAPI](https://fastapi.tiangolo.com/): it is a modern, fast web framework for building APIs with Python and provides compatibility with open standards such as OpenAPI. I have decided to choose FastAPI over Flask becouse it provides much better performance, it has native concurrency support and in-built data validation with [Pydantic](https://docs.pydantic.dev/). 
- [SQLAlchemy](https://www.sqlalchemy.org/): it is a Python SQL toolkit and Object Relational Mapper (ORM) that allows to convert ("map") between objects in code and database tables ("relations"). It supports multiple SQL databases such as PostgreSQL (the one selected for the code challenge).
- [Uvicorn](https://www.uvicorn.org/): it is an ASGI web server implementation for Python. It is used to run in a server the FastAPI application.

Since the book information is a structured data I decided to use a relational database. For the provided solution I decide to use [PostgreSQL](https://www.postgresql.org/) since it provides amazing performance, resiliency and scalability supporting replication for high-availabity (HA), fault-tolerance and load balancing purposes. 

The solution to this code challenge has been provided as a platform-agnostic container-based application (Docker). A container is a standard unit of software that allows to easily package up code including all the dependencies to run quickly and reliably across multiple computing environments. Aiming to simplify the deployment procedure the solution has been implemented for docker compose since it is easier to install and it is less resource-hungry than kubernetes. It is worth mentioning that the provided docker-compose.yml file can be easily migrated to a kubernetes manifest in order to take benefits of a kubernetes-based deployment to manage containerized applications at scale with its built-in self-healing, high reliability and autoscaling capabilities. As it is previously mentioned PostgreSQL supports replication and it can take benefit from kubernetes capabilities to do HA deployment of the database over kubernetes. 

## Project structure
The provided solution to the code challenge is structured as follows:

```bash
hpe_code_challenge
    ├── docker-compose.yml
    ├── .env
    ├── README.md
    └── src
        ├── Dockerfile
        ├── requirements.txt
        ├── app
        │   ├── __init__.py
        │   ├── config.py
        │   ├── database.py
        │   ├── models.py
        │   ├── schemas.py
        │   └── main.py
        └── test
            ├── __init__.py
            └── test_main.py
```

In the root folder of the project you can find the [docker-compose.yml](./docker-compose.yml) file which contains the docker compose service descriptor, the [.env](./.env) file containing the environment variables for the PostgreSQL database, the [README.md](./README.md) file and the [src](./src) folder where all the code is located.

Inside the [src](./src) folder you can find the [Dockerfile](./src/Dockerfile) of the app, the [requirements.txt](./src/requirements.txt) file with the python dependencies in addition to the [app](./src/app) and the [test](./src/test) directories containing the FastAPI code and the unit test code respectively. 

The [app](./src/app) folder contains [__init__.py](./src/app/__init__.py) file, the [config.py](./src/app/config.py) contains the code to make the PostgreSQL environment variables available for the FastAPI app using Pydantic, the [database.py](./src/app/database.py) contains the code to connect to the PostgreSQL database including the construction of the URL with the variables stored in the .env file and parsed with [config.py](./src/app/config.py). The [models.py](./src/app/models.py) file contains the SQLAlchemy models for the PostgreSQL database and the [schemas.py](./src/app/schemas.py) contains the Pydantic models the app will use to parse and validate the incoming requests and responses. The [main.py](./src/app/main.py) file contains all the FastAPI code for the four requested endpoints: GET /books, GET /books/{id}, POST /books and POST /reserve.

The [test](./src/test) folder contains the [__init__.py](./src/test/__init__.py) file and the [test_main.py](./src/test/test_main.py) file containing all the unit tests.

## Code comment
In the following lines a brief overivew of the application design and code decisions are explained:

### API design
The API endpoints are placed in [main.py](./src/app/main.py) file. Lets analize the different functions included in the applications:

1) get_books - this function searches and returns a list with all the available books in the catalogue with a HTTP 200 OK, if there are no books the list returned is empty. The time complexity of this function is dependant on the database.
2) get_book_by_id - this function searches and returns the book with the provided id. If the book exists it returns back the book with a HTTP 200 OK, if the book is not in the catalog it raises an HTTPException with error 400. The complexity of this function is also dependant on the database but for reducing the complexity as much as possible the id column has been indexed for search optimization purposes (more details in next subsection).
3) create_book - this function adds a new book to the catalogue with the attributes received as parameters. This functions benefits from the uniqueness of the isbn to detect duplicates (more details in next subsection), in case the isbn is already in the catalogue when being inserted SQLAlchemy raises a IntegrityError that is captured in order to perform a rollback and raise an HTTPException with error 400. The complexity of this function depends exclusively on the database insertion complexity.
4) reserve_book - this function reserves available books from a given list provided by parameter. The provided list can include repeated ids for reserving multiple copies of a book, in order to detect duplicates the provided list has been transformed to a python collection, more specifically a counter. A counter is a collection where elements are stored as dictionary keys and their counts are stored as dictionary values. The counter allows to detect the unique ids  in the list and the number of copies to be reserved per id. Then the function queries the books by the unique ids stored in the counter using the SQLAlchemy "with_for_update()" method to ensure data integrity, this method locks the row you want to change with a FOR UPDATE lock so another transactions have to wait until this transaction release the lock, the lock is released when a commit or rollback is performed. Once the books are obtained from the catalog the function compares the size of the list of books obtained in the query with the size of the counter (the number of unique ids), if the number is not the same it means that some ids do not exist then the function performs a rollback and raises an HTTPException with error 400. If the number is the same it means that all the ids are in the catalogue so the function checks if there is enough book copies in the catalog to reserve. If there are not enough copies of any book it performs a rollback and raises an HTTPException with error 400, if there are enough copies it performs a commit and finish the reservation transaction sending a HTTP 200 OK. Like in the previous methods the complexity of this function depends on the database but in this case the complexity will be at minimum O(n) due to the loop used in the implementation.

### Database design
As it is previously mentioned the database chosen for this code challenge is PostgreSQL. The model of the database structure have been defined in the [models.py](./src/app/models.py) file. Given the inputs provided in the code challenge the columns of the database are the following:

- id = Column(Integer, primary_key=True)
- title = Column(String, nullable=False)
- number_of_pages = Column(Integer, nullable=False)
- author = Column(String, nullable=False)
- isbn = Column(String(13), nullable=False, unique=True)
- number_of_copies = Column(Integer, nullable=False)
- available_copies = Column(Integer, nullable=False)

In order to optimize the search the id has been selected as primary key, enforcing the id to be unique and not null and automatically creating a unique btree index on this column. Since the id is used for searching in the get_books_by_id and reserve_book functions its indexation will accellerate the data retrieval compared to a not indexed column. I want to remark that the id provided in the code challenge report is an eight character alphanumeric variable in the form of a string and in order to optimize the space and the performance in PostgreSQL I have decided to substitute it with an Integer, aiming to reduce the overhead in the id for optimizing the query speed.

In similar way the isbn has been selected to be unique and not null (it is not a primary index since only one is allowerd per table). Adding a unique constraint also automatically creates a unique btree index on the column. The uniqueness of this column helps to avoid duplication of books into the catalogue and reduces the queries (it is not necessary to perform a query to check if the book is already in the catalogue), but the indexing of the column makes the insertion process a bit more costly.

Since the International Standard Book Number (ISBN) is already a unique identifier (each book has its own ISBN, in fact different editions of a book have different ISBNs) I think it would be better to eliminate the id and use the isbn as primary key and only index of the table. This decission will impact the API creation since the get_book_by_id and the reserve_book should be based on the isbn instead of the id.

### Data validation
In order to validate the data received and sent in the API I used Pydantic. The [schemas.py](./src/app/schemas.py) file contains the book models for the requests and the responses. With this data validation it is ensured that the id is a positive integer, the title is a string, the number of pages is a positive integer, the autor is a string, the ISBN is a string of 13 digits, the number of copies is a non negative integer and the available copies is a is a non negative integer.

## Prerequisities
In order to execute the provided solution it is necessary to install docker compose. The installation instructions of docker compose can be found in [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## Usage
In order to simplify the deployment a docker-compose.yml file is provided with two services:
 - app: containing the API server and the developed API
 - db: containing a PostgreSQL database instance

To deploy the docker compose just execute:
```bash
docker compose up -d --build
```
Once the solution is succesfully deployed with docker compose the OpenAPI schema of the developed API can be accessed in the following url: [http://127.0.0.1/docs](http://127.0.0.1/docs) 

To check the logs of all the services execute:
```bash
docker compose logs
```

To check the logs of the API execute:
```bash
docker compose logs app
```

To check the logs of the PostgreSQL database execute:
```bash
docker compose logs db
```

To stop the docker compose execute:
```bash
docker compose down
```

## Testing
For testing the API I have used [Startlette](https://www.starlette.io/) which allows to directly use pytest with FastAPI.
To execute the unit test execute the following command:
```bash
docker compose exec app coverage run -m pytest -v
```

To visualize the code coverage report execute the following command after running the unit tests:
```bash
docker compose exec app coverage report
```