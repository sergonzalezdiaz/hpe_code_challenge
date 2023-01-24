from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt

class BookBaseSchema(BaseModel):
    """Book schema for the creation request without the id"""
    title: str
    number_of_pages: PositiveInt
    author: str
    isbn: str = Field(max_length=13)
    number_of_copies: NonNegativeInt
    available_copies: NonNegativeInt

class BookResponseSchema(BaseModel):
    """Book schema for the responses including the id"""
    id: PositiveInt
    title: str
    number_of_pages: PositiveInt
    author: str
    isbn: str = Field(max_length=13)
    number_of_copies: NonNegativeInt
    available_copies: NonNegativeInt

    class Config:
        orm_mode = True