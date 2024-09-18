import pytest
from fastapi.testclient import TestClient
from main import app
from db.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from schemas.pydantic_models.book_model import Book, UpdateBook
from schemas.pydantic_models.user_schema import UserCreate, User
from security.auth import create_access_token
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"


@pytest.fixture(scope="module")
async def db_session():
    async_engine = create_async_engine(DATABASE_URL, echo=True)

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Basic root endpoint test
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Book Catalog API"}

# User creation tests
@pytest.mark.asyncio
async def test_create_user(client, db_session):
    new_user = UserCreate(username="user1", email="user1@example.com", password="testpassword")
    response = client.post("/users/", json=new_user.dict())
    assert response.status_code == 201
    assert response.json()["username"] == "user1"
    assert response.json()["email"] == "user1@example.com"

@pytest.mark.asyncio
async def test_create_user_with_existing_username(client, db_session):
    new_user = UserCreate(username="user2", email="uniqueuser@example.com", password="testpassword")
    response = client.post("/users/", json=new_user.dict())
    assert response.status_code == 201

    duplicate_user = UserCreate(username="user2", email="anotheruser@example.com", password="testpassword")
    response = client.post("/users/", json=duplicate_user.dict())
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists."

@pytest.mark.asyncio
async def test_create_user_with_existing_email(client, db_session):
    new_user = UserCreate(username="uniqueuser", email="user3@example.com", password="testpassword")
    response = client.post("/users/", json=new_user.dict())
    assert response.status_code == 201

    duplicate_user = UserCreate(username="anotheruser", email="user3@example.com", password="testpassword")
    response = client.post("/users/", json=duplicate_user.dict())
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered."

@pytest.mark.asyncio
async def test_create_user_with_missing_fields(client, db_session):
    incomplete_user = {"username": "incompleteuser"}
    response = client.post("/users/", json=incomplete_user)
    assert response.status_code == 422
    assert "detail" in response.json()

# User login test
@pytest.mark.asyncio
async def test_user_login(client, db_session):
    new_user = UserCreate(username="user4", email="user4@example.com", password="testpassword")
    response = client.post("/users/", json=new_user.dict())
    assert response.status_code == 201

    login_data = User(username="user4", password="testpassword")
    response = client.post("/token/", data=login_data.dict())
    assert response.status_code == 200
    assert "access_token" in response.json()

# Book creation tests
@pytest.mark.asyncio
async def test_create_book(client, db_session):
    user_data = UserCreate(username="user5", email="user5@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}

    new_book = Book(
        title="Book1", author="Author1", isbn="1234567890", publication_year=2023
    )
    response = client.post("/books/", json=new_book.dict(), headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Book1"

@pytest.mark.asyncio
async def test_create_book_with_missing_fields(client, db_session):
    user_data = UserCreate(username="user6", email="user6@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}

    incomplete_book = {"title": "Incomplete Book"}
    response = client.post("/books/", json=incomplete_book, headers=headers)
    assert response.status_code == 422
    assert "detail" in response.json()

# Book retrieval tests
@pytest.mark.asyncio
async def test_get_books(client, db_session):
    user_data = UserCreate(username="user7", email="user7@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/books/", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_book(client, db_session):
    new_book = Book(
        title="Book2", author="Author2", isbn="1234567891", publication_year=2023
    )
    user_data = UserCreate(username="user8", email="user8@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/books/", json=new_book.dict(), headers=headers)
    assert response.status_code == 201
    book_id = response.json()["id"]

    response = client.get(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Book2"

@pytest.mark.asyncio
async def test_get_nonexistent_book(client, db_session):
    user_data = UserCreate(username="user9", email="user9@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/books/999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

@pytest.mark.asyncio
async def test_get_books_unauthorized(client):
    response = client.get("/books/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Book update tests
@pytest.mark.asyncio
async def test_update_book(client, db_session):
    new_book = Book(
        title="Book3", author="Author3", isbn="1234567892", publication_year=2023
    )
    user_data = UserCreate(username="user10", email="user10@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/books/", json=new_book.dict(), headers=headers)
    assert response.status_code == 201
    book_id = response.json()["id"]

    updated_book = UpdateBook(title="Updated Book3")
    response = client.put(f"/books/{book_id}", json=updated_book.dict(), headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Book3"

@pytest.mark.asyncio
async def test_update_nonexistent_book(client, db_session):
    user_data = UserCreate(username="user11", email="user11@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}

    updated_book = {"title": "Nonexistent Book"}
    response = client.put("/books/999999", json=updated_book, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

@pytest.mark.asyncio
async def test_update_book_unauthorized(client):
    updated_book = {"title": "Unauthorized Update"}
    response = client.put("/books/1", json=updated_book)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Book deletion tests
@pytest.mark.asyncio
async def test_delete_book(client, db_session):
    new_book = Book(
        title="Book4", author="Author4", isbn="1234567893", publication_year=2023
    )
    user_data = UserCreate(username="user12", email="user12@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/books/", json=new_book.dict(), headers=headers)
    assert response.status_code == 201
    book_id = response.json()["id"]

    response = client.delete(f"/books/{book_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Book deleted successfully"

@pytest.mark.asyncio
async def test_delete_nonexistent_book(client, db_session):
    user_data = UserCreate(username="user13", email="user13@example.com", password="testpassword")
    response = client.post("/users/", json=user_data.dict())
    assert response.status_code == 201

    user = response.json()
    access_token = create_access_token(data={"sub": user["username"]})
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.delete("/books/999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

@pytest.mark.asyncio
async def test_delete_book_unauthorized(client):
    response = client.delete("/books/1")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
