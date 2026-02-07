from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, validator
from sqlmodel import Session, select
from typing import Optional
import re
import logging

from ..models.user_model import User
from ..auth.password import hash_password, verify_password
from ..auth.jwt_handler import JWTHandler
from ..database.database import get_session
from ..config import get_settings

# Setup logging
logger = logging.getLogger(__name__)

# Get settings for JWT configuration
settings = get_settings()
jwt_handler = JWTHandler(secret_key=settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


# ============================================================================
# Request/Response Schemas
# ============================================================================

class SignupRequest(BaseModel):
    """
    Request schema for user signup.

    Validates email format, password complexity, and name requirements.
    """
    email: EmailStr
    password: str
    name: str

    @validator('password')
    def validate_password(cls, v):
        """
        Validate password complexity requirements.

        Requirements:
        - Minimum 8 characters
        - At least one letter (a-z or A-Z)
        - At least one number (0-9)
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('name')
    def validate_name(cls, v):
        """
        Validate name is non-empty after stripping whitespace.
        """
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class LoginRequest(BaseModel):
    """
    Request schema for user login.

    Minimal validation - actual credential verification happens during authentication.
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Response schema for user data (excludes sensitive information).

    Never includes password or password_hash.
    """
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True  # Allows creation from SQLModel instances


class AuthResponse(BaseModel):
    """
    Response schema for successful authentication (signup or login).

    Returns JWT token and user information.
    """
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================================
# Signup Endpoint (User Story 1)
# ============================================================================

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    Creates a new user with email, password, and name. Returns JWT token for immediate use.

    Args:
        signup_data: User registration data (email, password, name)
        session: Database session

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Validation error (weak password, empty name)
        HTTPException 422: Invalid email format (handled by Pydantic)
    """
    try:
        # T012: Check if email already exists in database
        statement = select(User).where(User.email == signup_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            # T017: Return 409 Conflict for duplicate email
            logger.warning(f"Signup attempt with existing email: {signup_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # T013: Hash password using bcrypt
        password_hash = hash_password(signup_data.password)

        # T014: Create User record in database
        new_user = User(
            email=signup_data.email,
            password_hash=password_hash,
            name=signup_data.name
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # T015: Generate JWT token
        access_token = jwt_handler.create_access_token(
            user_id=new_user.id,
            email=new_user.email
        )

        # T019: Log successful signup (never log passwords)
        logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

        # T016: Return 201 Created with AuthResponse
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name
            )
        )

    except HTTPException:
        # Re-raise HTTP exceptions (409 Conflict)
        raise

    except ValueError as e:
        # T018: Handle validation errors from Pydantic validators
        logger.warning(f"Signup validation error for {signup_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # T019: Log unexpected errors
        logger.error(f"Signup error for {signup_data.email}: {str(e)}")
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


# ============================================================================
# Login Endpoint (User Story 2)
# ============================================================================

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate an existing user.

    Verifies email and password, returns JWT token if credentials are valid.

    Args:
        login_data: User login credentials (email, password)
        session: Database session

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        HTTPException 401: Invalid credentials (wrong password or email not found)
        HTTPException 422: Invalid email format (handled by Pydantic)
    """
    try:
        # T022: Query database for User by email
        statement = select(User).where(User.email == login_data.email)
        user = session.exec(statement).first()

        # T023: If user not found, return 401 with generic message (no user enumeration)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # T024: Verify password using verify_password()
        is_valid = verify_password(login_data.password, user.password_hash)

        # T025: If password verification fails, return 401 with generic message
        if not is_valid:
            logger.warning(f"Login attempt with invalid password for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # T026: Generate JWT token
        access_token = jwt_handler.create_access_token(
            user_id=user.id,
            email=user.email
        )

        # T028: Log successful login (never log passwords)
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")

        # T027: Return 200 OK with AuthResponse
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name
            )
        )

    except HTTPException:
        # Re-raise HTTP exceptions (401 Unauthorized)
        raise

    except Exception as e:
        # T029: Handle database errors and return 500 Internal Server Error
        logger.error(f"Login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


# Endpoints for User Story 3 will be verified in subsequent tasks
