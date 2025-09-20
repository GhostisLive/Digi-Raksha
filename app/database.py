from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional
import io
import uuid
from fastapi import UploadFile

# Load environment variables
load_dotenv()

# Environment variables
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase

class SupabaseStorage:
    """Helper class for Supabase storage operations"""
    
    def __init__(self):
        self.client = supabase
        self.buckets = {
            'profile_photos': 'profile-photos',
            'incident_photos': 'incident-photos',
            'missing_person_photos': 'missing-person-photos',
            'community_photos': 'community-photos'
        }
    
    async def upload_file(self, file: UploadFile, bucket_name: str, folder: str = "") -> str:
        """
        Upload a file to Supabase Storage
        
        Args:
            file: FastAPI UploadFile object
            bucket_name: Name of the storage bucket
            folder: Optional folder within bucket
            
        Returns:
            str: URL of the uploaded file
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"{folder}/{unique_filename}" if folder else unique_filename
            
            # Read file content
            file_content = await file.read()
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": file.content_type,
                    "cache-control": "3600"
                }
            )
            
            if response.status_code == 200:
                # Get public URL
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
                return public_url
            else:
                raise Exception(f"Upload failed: {response}")
                
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")
    
    async def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """
        Delete a file from Supabase Storage
        
        Args:
            bucket_name: Name of the storage bucket
            file_path: Path of the file to delete
            
        Returns:
            bool: True if successful
        """
        try:
            response = self.client.storage.from_(bucket_name).remove([file_path])
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_url(self, bucket_name: str, file_path: str) -> str:
        """
        Get public URL for a file
        
        Args:
            bucket_name: Name of the storage bucket
            file_path: Path of the file
            
        Returns:
            str: Public URL of the file
        """
        return self.client.storage.from_(bucket_name).get_public_url(file_path)
    
    async def ensure_buckets_exist(self):
        """Create storage buckets if they don't exist"""
        try:
            # List existing buckets
            existing_buckets = self.client.storage.list_buckets()
            existing_bucket_names = [bucket.name for bucket in existing_buckets]
            
            # Create missing buckets
            for bucket_key, bucket_name in self.buckets.items():
                if bucket_name not in existing_bucket_names:
                    self.client.storage.create_bucket(
                        bucket_name,
                        options={
                            "public": True,
                            "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp"],
                            "file_size_limit": 10485760  # 10MB
                        }
                    )
                    print(f"Created bucket: {bucket_name}")
                    
        except Exception as e:
            print(f"Error ensuring buckets exist: {str(e)}")

# Initialize storage helper
storage = SupabaseStorage()