import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt
from datetime import timedelta
import logging
from db.models import User
from schemas.pydantic_models.user_schema import UserCreate
from db.database import get_session
from security.auth import authenticate_user, Token
from utilities.utils import create_access_token

auth_router = APIRouter()

def get_email_config() -> Dict[str, str]:
    return {
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
        "MAIL_FROM": os.getenv("MAIL_FROM"),
        "MAIL_PORT": int(os.getenv("MAIL_PORT")),
        "MAIL_SERVER": os.getenv("MAIL_SERVER"),
    }

def send_email(recipient: str, subject: str, html: str):
    email_config = get_email_config()
    try:
        # Setup the MIME
        message = MIMEMultipart()
        message["From"] = email_config["MAIL_FROM"]
        message["To"] = recipient
        message["Subject"] = subject

        # Attach HTML body
        message.attach(MIMEText(html, "html"))

        # Connect to SMTP server
        with smtplib.SMTP(email_config["MAIL_SERVER"], email_config["MAIL_PORT"]) as server:
            server.starttls()
            server.login(email_config["MAIL_USERNAME"], email_config["MAIL_PASSWORD"])
            server.send_message(message)
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@auth_router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, session=Depends(get_session)):
    try:
        existing_user = session.execute(select(User).filter(User.username == user.username))
        if existing_user.scalars().first():
            raise HTTPException(status_code=400, detail="Username already registered")

        password = user.password
        new_user = User(username=user.username, email=user.email, password=password, is_active=False)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Create verification token
        verification_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(hours=24)
        )

        # Create and send verification email
        verification_link = f"http://127.0.0.1:8080/verify?token={verification_token}"
        html = f"""
        <p>Hi {user.username},</p>
        <p>Please click the link below to verify your email address:</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p>This link will expire in 24 hours.</p>
        """
        send_email(user.email, "Verify Your Email", html)

        # Create JWT token for further actions
        access_token = create_access_token(data={"sub": user.username, "role": "user"})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        session.rollback()
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@auth_router.get("/verify")
def verify_email(token: str, session=Depends(get_session)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid verification token")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    user = session.execute(select(User).filter(User.email == email))
    user = user.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        return {"message": "Email already verified"}

    user.is_active = True
    session.commit()
    return {"message": "Email verified successfully"}





@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    try:
        # Authenticate user with plain text password
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create JWT token
        access_token = create_access_token(data={"sub": user.username, "role": "admin" if user.is_admin else "user"})

        # Set the token in a cookie
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Lax")
        return response

    except Exception as e:
        logging.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

