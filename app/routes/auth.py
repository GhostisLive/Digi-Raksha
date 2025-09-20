from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Optional
from app.models.user import UserCreate, UserLogin, User, Token
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.database import get_supabase_client, storage
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(None),
    city: str = Form(...),
    phone_number: str = Form(...),
    gov_id_type: str = Form(...),
    gov_id_number: str = Form(...),
    password: str = Form(...),
    photo: UploadFile = File(None)
):
    """Register a new user with optional photo upload"""
    supabase = get_supabase_client()
    
    # Check if user already exists
    existing_user = supabase.table("users").select("*").eq("gov_id_number", gov_id_number).execute()
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this government ID already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(password)
    
    # Handle photo upload
    photo_url = None
    if photo and photo.filename:
        try:
            # Validate file type
            if not photo.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be an image"
                )
            
            # Upload photo to Supabase Storage
            photo_url = await storage.upload_file(
                file=photo,
                bucket_name=storage.buckets['profile_photos'],
                folder=f"users/{gov_id_number}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo: {str(e)}"
            )
    
    # Create user data
    user_data = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "city": city,
        "phone_number": phone_number,
        "gov_id_type": gov_id_type,
        "gov_id_number": gov_id_number,
        "password_hash": hashed_password,
        "photo_url": photo_url
    }
    
    # Insert user into database
    result = supabase.table("users").insert(user_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": gov_id_number}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user"""
    supabase = get_supabase_client()
    
    # Get user from database
    user_result = supabase.table("users").select("*").eq("gov_id_number", user_credentials.gov_id_number).execute()
    
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = user_result.data[0]
    
    # Verify password
    if not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["gov_id_number"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/upload-photo")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload or update user profile photo"""
    try:
        # Validate file type
        if not photo.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Upload photo to Supabase Storage
        photo_url = await storage.upload_file(
            file=photo,
            bucket_name=storage.buckets['profile_photos'],
            folder=f"users/{current_user['gov_id_number']}"
        )
        
        # Update user record with new photo URL
        supabase = get_supabase_client()
        result = supabase.table("users").update({"photo_url": photo_url}).eq("id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user photo"
            )
        
        return {"photo_url": photo_url, "message": "Photo uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload photo: {str(e)}"
        )