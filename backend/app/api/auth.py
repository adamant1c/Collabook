from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, verify_token, generate_reset_token
from app.core.rpg_stats import initialize_character_stats
from app.core.security_utils import sanitize_user_input, validate_email_format
from app.models.db_models import User, UserRole
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.schemas import UserRegister, UserLogin, Token, UserResponse, PasswordResetRequest, PasswordReset

def send_email(to_email: str, subject: str, content: str):
    """Send email via SMTP (configured for Mailhog or external)"""
    smtp_server = os.getenv("SMTP_SERVER", "mailhog")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    sender_email = os.getenv("SMTP_SENDER", "noreply@collabook.com")
    
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain"))
    
    try:
        # Connect to server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        
        # Enable TLS if using port 587 (Gmail)
        if smtp_port == 587:
            server.starttls()
            server.ehlo()
            
        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)
            
        server.send_message(msg)
        server.quit()
        
        print(f"📧 Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("50/hour")  # Max 50 registrations per hour per IP
async def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new player account (rate limited: 3/hour)"""
    
    # Sanitize inputs
    username = sanitize_user_input(user_data.username, max_length=50)
    name = sanitize_user_input(user_data.name, max_length=100)
    
    # Extra email validation
    if not validate_email_format(user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(
        username=username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=UserRole.PLAYER,
        name=name,
        profession=user_data.profession,
        description=user_data.description,
        avatar_description=user_data.avatar_description,
        is_active=False  # Verification required
    )
    
    # Initialize RPG stats (random 1-10)
    initialize_character_stats(db_user)
    
    # Generate verification token (reusing reset_token logic for simplicity)
    verification_token = generate_reset_token()
    db_user.reset_token = verification_token
    db_user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email (Mock)
    # Frontend URLs for accounts are at root path (""), so use /verify-email/
    verification_link = f"http://localhost:8501/verify-email/?token={verification_token}"
    
    email_body = f"""
    Welcome to Collabook, {db_user.username}!
    
    Please click the link below to verify your account:
    {verification_link}
    
    If you did not request this, please ignore this email.
    """
    
    send_email(db_user.email, "Verify your Collabook Account", email_body)
    print(f"📧 [DEBUG] Verification link: {verification_link}")
    
    return {"message": "Registration successful. Please check your email to verify your account."}

@router.post("/login", response_model=Token)
@limiter.limit("100/minute")  # Max 100 login attempts per minute per IP
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password (rate limited: 5/minute)"""
    
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/request-reset")
@limiter.limit("50/hour")  # Max 50 password reset requests per hour per IP
async def request_password_reset(request: Request, reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset (rate limited: 3/hour)"""
    
    user = db.query(User).filter(User.email == reset_request.email).first()
    
    if not user:
        # Don't reveal if email exists (security)
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token (valid for 1 hour)
    reset_token = generate_reset_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    
    db.commit()
    
    # Send email with reset link
    reset_link = f"http://localhost:8501/reset-password?token={reset_token}"
    
    email_body = f"""
    Hello,
    
    You have requested to reset your password for Collabook.
    Please click the link below to reset it:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you did not request this, please ignore this email.
    """
    
    send_email(user.email, "Collabook Password Reset", email_body)
    print(f"📧 [DEBUG] Password reset email sent to {user.email}")
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Reset password using token"""
    
    user = db.query(User).filter(User.reset_token == reset_data.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    if user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    user.password_hash = hash_password(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password successfully reset"}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email address using token"""
    
    user = db.query(User).filter(User.reset_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
        
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
        
    # Activate user
    user.is_active = True
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Email verified successfully"}
