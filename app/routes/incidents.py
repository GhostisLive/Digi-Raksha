from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from app.models.incident import IncidentCreate, Incident
from app.auth import get_current_user
from app.database import get_supabase_client, storage

router = APIRouter()

@router.post("/", response_model=Incident)
async def create_incident(
    incident_type: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """Create a new incident report with optional photo upload"""
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
                bucket_name=storage.buckets['incident_photos'],
                folder=f"incidents/{current_user['id']}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload photo: {str(e)}"
            )
    
    incident_data = {
        "user_id": current_user["id"],
        "incident_type": incident_type,
        "description": description,
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "photo_url": photo_url,
        "status": "reported"
    }
    
    result = supabase.table("incidents").insert(incident_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create incident report"
        )
    
    return result.data[0]

@router.get("/", response_model=List[Incident])
async def get_incidents(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all incident reports"""
    supabase = get_supabase_client()
    
    result = supabase.table("incidents").select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
    
    return result.data

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific incident by ID"""
    supabase = get_supabase_client()
    
    result = supabase.table("incidents").select("*").eq("id", incident_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return result.data[0]

@router.put("/{incident_id}/status")
async def update_incident_status(incident_id: str, status_update: str, current_user: dict = Depends(get_current_user)):
    """Update incident status (for admin use)"""
    supabase = get_supabase_client()
    
    result = supabase.table("incidents").update({"status": status_update}).eq("id", incident_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return {"message": "Incident status updated successfully"}