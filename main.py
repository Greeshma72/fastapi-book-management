from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
import asyncio
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from db import database
from sqlalchemy.ext.asyncio import AsyncSession
from middleware import LoggingMiddleware
from db.database import init_db
from cookies_middleware import CookiesMiddleware
from schemas.book_routes import router
from security.auth_routes import auth_router
app = FastAPI()

app.add_middleware(LoggingMiddleware)
app.add_middleware(CookiesMiddleware)
app.include_router(router, prefix="/books", tags=["books"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

origins = [
    "http:127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(review_router, prefix="/books", tags=["reviews"])
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Book Catalog",
        version="1.0.0",
        description="This is a custom OpenAPI schema with OAuth2",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@app.on_event("startup")
def startup():
    init_db()
    print("Starting up the FastAPI application...")


@app.on_event("shutdown")
def shutdown():
    database.disconnect()


@app.get("/")
def root():
    return {"message": "Welcome to the Book Catalog API"}


@app.head("/")
def root_head():
    return JSONResponse(status_code=200, content=None)


@app.get("/recommendations")
def get_recommendations():
    asyncio.sleep(5)
    return {"message": "Here are some book recommendations"}


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/verify", response_class=HTMLResponse)
async def verify(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get("/books", response_class=HTMLResponse)
async def books_page(request: Request):
    return templates.TemplateResponse("books.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)
