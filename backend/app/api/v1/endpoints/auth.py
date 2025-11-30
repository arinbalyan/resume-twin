"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# Placeholder models for now
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint."""
    # TODO: Implement Supabase authentication
    raise HTTPException(status_code=501, detail="Login not implemented yet")


@router.post("/register")
async def register(request: RegisterRequest):
    """User registration endpoint."""
    # TODO: Implement Supabase authentication
    raise HTTPException(status_code=501, detail="Registration not implemented yet")


@router.post("/logout")
async def logout():
    """User logout endpoint."""
    # TODO: Implement logout
    raise HTTPException(status_code=501, detail="Logout not implemented yet")


@router.get("/me")
async def get_current_user():
    """Get current user information."""
    # TODO: Implement user retrieval
    raise HTTPException(status_code=501, detail="User info not implemented yet")