from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.community import CommunityPostCreate, CommunityPost
from app.auth import get_current_user
from app.database import get_supabase_client

router = APIRouter()

@router.post("/", response_model=CommunityPost)
async def create_community_post(post: CommunityPostCreate, current_user: dict = Depends(get_current_user)):
    """Create a new community post"""
    supabase = get_supabase_client()
    
    post_data = {
        "user_id": current_user["id"],
        "user_name": f"{current_user['first_name']} {current_user['last_name']}",
        "category": post.category.value,
        "message": post.message,
        "location": post.location
    }
    
    result = supabase.table("community_posts").insert(post_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create community post"
        )
    
    return result.data[0]

@router.get("/", response_model=List[CommunityPost])
async def get_community_posts(skip: int = 0, limit: int = 100, category: str = None, current_user: dict = Depends(get_current_user)):
    """Get all community posts"""
    supabase = get_supabase_client()
    
    query = supabase.table("community_posts").select("*")
    
    if category:
        query = query.eq("category", category)
    
    result = query.range(skip, skip + limit - 1).order("created_at", desc=True).execute()
    
    return result.data

@router.get("/{post_id}", response_model=CommunityPost)
async def get_community_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific community post by ID"""
    supabase = get_supabase_client()
    
    result = supabase.table("community_posts").select("*").eq("id", post_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post not found"
        )
    
    return result.data[0]

@router.delete("/{post_id}")
async def delete_community_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a community post (only by the author)"""
    supabase = get_supabase_client()
    
    # Check if the post exists and belongs to the current user
    post_result = supabase.table("community_posts").select("*").eq("id", post_id).eq("user_id", current_user["id"]).execute()
    
    if not post_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community post not found or you don't have permission to delete it"
        )
    
    # Delete the post
    result = supabase.table("community_posts").delete().eq("id", post_id).execute()
    
    return {"message": "Community post deleted successfully"}