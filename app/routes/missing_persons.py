from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from app.models.missing_person import MissingPersonCreate, MissingPerson
from app.auth import get_current_user
from app.database import get_supabase_client, storage

router = APIRouter()

@router.post("/", response_model=MissingPerson)
async def report_missing_person(
    name: str = Form(...),
    age: int = Form(...),
    last_seen_location: str = Form(...),
    description: str = Form(...),
    reporter_contact: str = Form(...),
    photo: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Report a missing person with optional photo upload"""
    supabase = get_supabase_client()
    
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
                bucket_name=storage.buckets['missing_person_photos'],
                folder=f"missing/{current_user['id']}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo: {str(e)}"
            )
    
    missing_person_data = {
        "user_id": current_user["id"],
        "name": name,
        "age": age,
        "last_seen_location": last_seen_location,
        "description": description,
        "reporter_contact": reporter_contact,
        "photo_url": photo_url,
        "status": "missing"
    }
    
    result = supabase.table("missing_persons").insert(missing_person_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report missing person"
        )
    
    return result.data[0]

@router.get("/", response_model=List[MissingPerson])
async def get_missing_persons(skip: int = 0, limit: int = 100, search: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Get all missing persons reports"""
    supabase = get_supabase_client()
    
    query = supabase.table("missing_persons").select("*")
    
    if search:
        # Search by name (case-insensitive)
        query = query.ilike("name", f"%{search}%")
    
    result = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
    
    return result.data

@router.get("/{missing_person_id}", response_model=MissingPerson)
async def get_missing_person(missing_person_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific missing person by ID"""
    supabase = get_supabase_client()
    
    result = supabase.table("missing_persons").select("*").eq("id", missing_person_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Missing person report not found"
        )
    
    return result.data[0]

@router.put("/{missing_person_id}/status")
async def update_missing_person_status(missing_person_id: str, status_update: str, current_user: dict = Depends(get_current_user)):
    """Update missing person status"""
    supabase = get_supabase_client()
    
    result = supabase.table("missing_persons").update({"status": status_update}).eq("id", missing_person_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Missing person report not found"
        )
    
    return {"message": "Missing person status updated successfully"}