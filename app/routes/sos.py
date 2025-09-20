from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.sos import SOSCreate, SOSAlert, SafeStatusUpdate
from app.auth import get_current_user
from app.database import get_supabase_client

router = APIRouter()

@router.post("/", response_model=SOSAlert)
async def create_sos_alert(sos: SOSCreate, current_user: dict = Depends(get_current_user)):
    """Create a new SOS alert"""
    supabase = get_supabase_client()
    
    # Check if user has an active SOS alert
    existing_sos = supabase.table("sos_alerts").select("*").eq("user_id", current_user["id"]).eq("status", "active").execute()
    
    if existing_sos.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active SOS alert"
        )
    
    sos_data = {
        "user_id": current_user["id"],
        "user_name": f"{current_user['first_name']} {current_user['last_name']}",
        "latitude": sos.latitude,
        "longitude": sos.longitude,
        "location_description": sos.location_description,
        "emergency_type": sos.emergency_type,
        "status": "active"
    }
    
    result = supabase.table("sos_alerts").insert(sos_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SOS alert"
        )
    
    return result.data[0]

@router.get("/", response_model=List[SOSAlert])
async def get_sos_alerts(skip: int = 0, limit: int = 100, current_user: dict = Depends(get_current_user)):
    """Get all active SOS alerts"""
    supabase = get_supabase_client()
    
    result = supabase.table("sos_alerts").select("*").eq("status", "active").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
    
    return result.data

@router.get("/nearby")
async def get_nearby_sos_alerts(latitude: float, longitude: float, radius_km: float = 10, current_user: dict = Depends(get_current_user)):
    """Get nearby SOS alerts within specified radius"""
    supabase = get_supabase_client()
    
    # For simplicity, we'll get all active alerts and filter by distance in the application
    # In production, you'd want to use PostGIS or similar for proper geospatial queries
    result = supabase.table("sos_alerts").select("*").eq("status", "active").execute()
    
    # Basic distance filtering (this should be done in the database for better performance)
    nearby_alerts = []
    for alert in result.data:
        # Simple distance calculation (you may want to use a proper geospatial library)
        lat_diff = abs(alert["latitude"] - latitude)
        lon_diff = abs(alert["longitude"] - longitude)
        if lat_diff <= radius_km/111 and lon_diff <= radius_km/111:  # Rough approximation
            nearby_alerts.append(alert)
    
    return nearby_alerts

@router.post("/safe")
async def mark_safe(safe_status: SafeStatusUpdate, current_user: dict = Depends(get_current_user)):
    """Mark user as safe and resolve any active SOS alerts"""
    supabase = get_supabase_client()
    
    # Update any active SOS alerts for this user
    result = supabase.table("sos_alerts").update({"status": "resolved"}).eq("user_id", current_user["id"]).eq("status", "active").execute()
    
    # You could also create a "safe status" record here if needed
    safe_record = {
        "user_id": current_user["id"],
        "user_name": f"{current_user['first_name']} {current_user['last_name']}",
        "latitude": safe_status.latitude,
        "longitude": safe_status.longitude,
        "message": safe_status.message
    }
    
    supabase.table("safe_status").insert(safe_record).execute()
    
    return {"message": "Marked as safe successfully"}

@router.put("/{sos_id}/status")
async def update_sos_status(sos_id: str, status_update: str, current_user: dict = Depends(get_current_user)):
    """Update SOS alert status"""
    supabase = get_supabase_client()
    
    result = supabase.table("sos_alerts").update({"status": status_update}).eq("id", sos_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SOS alert not found"
        )
    
    return {"message": "SOS alert status updated successfully"}