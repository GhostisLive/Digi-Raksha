from fastapi import FastAPI, Form, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from supabase import create_client, Client
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import uuid
from typing import Optional
import io

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # In production, environment variables are set by the hosting platform
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Digi-रक्षा API",
    description="Backend API for Digi-रक्षा disaster management application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, SECRET_KEY]):
    raise Exception("Missing required environment variables")

# Use service key for backend operations to bypass RLS
supabase_key = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, supabase_key)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def upload_image_to_supabase(file: UploadFile, bucket_name: str, folder: str = "") -> str:
    """Upload an image to Supabase storage and return the public URL"""
    try:
        if not file:
            return None
            
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{unique_filename}" if folder else unique_filename
        
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase storage
        result = supabase.storage.from_(bucket_name).upload(file_path, file_content)
        
        if result:
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            return public_url
        else:
            return None
            
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

# Routes
@app.get("/")
async def root():
    """Serve the main HTML page"""
    try:
        with open("static/main.html", "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse("<h1>Welcome to Digi-रक्षा</h1><p>Main HTML file not found</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Digi-रक्षा API is running successfully"}

@app.post("/api/auth/register")
async def register(
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(""),
    city: str = Form(...),
    phone_number: str = Form(...),
    gov_id_type: str = Form(...),
    gov_id_number: str = Form(...),
    password: str = Form(...),
    photo: UploadFile = File(None)
):
    """Register a new user"""
    try:
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
            photo_url = await upload_image_to_supabase(photo, "profile_pictures", "users")
            if not photo_url:
                # Don't fail registration if photo upload fails, just log it
                print("Warning: Failed to upload profile picture")
        
        # Create user data
        user_data = {
            "first_name": first_name,
            "middle_name": middle_name if middle_name else None,
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
        access_token = create_access_token(data={"sub": gov_id_number})
        
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "message": "User registered successfully",
            "user_id": result.data[0]["id"],
            "photo_uploaded": bool(photo_url)
        }
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/api/auth/login")
async def login(
    gov_id_number: str = Form(...),
    password: str = Form(...)
):
    """Login user"""
    try:
        # Get user from database
        user_result = supabase.table("users").select("*").eq("gov_id_number", gov_id_number).execute()
        
        if not user_result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user = user_result.data[0]
        
        # Verify password
        if not verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user["gov_id_number"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "city": user["city"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.get("/api/users")
async def get_users():
    """Get all users (for testing)"""
    try:
        result = supabase.table("users").select("id, first_name, last_name, city, gov_id_type, created_at").execute()
        return {"users": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@app.post("/api/incidents")
async def create_incident(
    incident_type: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    user_id: str = Form(...),
    incident_image: UploadFile = File(None)
):
    """Create a new incident report"""
    try:
        print(f"[{datetime.now()}] Starting incident creation...")
        
        # Handle image upload
        photo_url = None
        if incident_image and incident_image.filename:
            print(f"[{datetime.now()}] Uploading image: {incident_image.filename}")
            photo_url = await upload_image_to_supabase(incident_image, "incident_images", "reports")
            print(f"[{datetime.now()}] Image uploaded successfully: {photo_url}")
        else:
            print(f"[{datetime.now()}] No image provided")
        
        # Create incident data
        incident_data = {
            "user_id": user_id,
            "incident_type": incident_type,
            "description": description,
            "location": location,
            "status": "reported"
        }
        
        # Add photo_url if we have one
        if photo_url:
            incident_data["photo_url"] = photo_url
            print(f"[{datetime.now()}] Added photo_url to incident_data: {photo_url}")
        
        print(f"[{datetime.now()}] Inserting to database: {incident_data}")
        result = supabase.table("incidents").insert(incident_data).execute()
        print(f"[{datetime.now()}] Database response: {result.data}")
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create incident"
            )
        
        return {
            "message": "Incident reported successfully", 
            "incident_id": result.data[0]["id"],
            "image_uploaded": bool(photo_url),
            "image_url": photo_url if photo_url else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )

@app.get("/api/incidents")
async def get_incidents():
    """Get all incidents"""
    try:
        result = supabase.table("incidents").select("*").order("created_at", desc=True).execute()
        return {"incidents": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch incidents: {str(e)}"
        )

@app.post("/api/missing")
async def create_missing_person(
    name: str = Form(...),
    age: int = Form(...),
    last_seen_location: str = Form(...),
    description: str = Form(...),
    reporter_contact: str = Form(...),
    user_id: str = Form(...),
    person_photo: UploadFile = File(None)
):
    """Report a missing person"""
    try:
        # Handle photo upload
        photo_url = None
        if person_photo and person_photo.filename:
            photo_url = await upload_image_to_supabase(person_photo, "missing_person_photos", "reports")
        
        missing_data = {
            "user_id": user_id,
            "name": name,
            "age": age,
            "last_seen_location": last_seen_location,
            "description": description,
            "reporter_contact": reporter_contact,
            "status": "missing",
            "photo_url": photo_url
        }
        
        result = supabase.table("missing_persons").insert(missing_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create missing person report"
            )
        
        return {
            "message": "Missing person reported successfully", 
            "report_id": result.data[0]["id"],
            "photo_uploaded": bool(photo_url)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create missing person report: {str(e)}"
        )

@app.get("/api/missing")
async def get_missing_persons():
    """Get all missing persons"""
    try:
        result = supabase.table("missing_persons").select("*").eq("status", "missing").order("created_at", desc=True).execute()
        return {"missing_persons": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch missing persons: {str(e)}"
        )

@app.post("/api/community")
async def create_community_post(
    category: str = Form(...),
    message: str = Form(...),
    location: str = Form(...),
    user_name: str = Form(...),
    user_id: str = Form(...),
    post_image: UploadFile = File(None)
):
    """Create a community post"""
    try:
        # Handle image upload
        image_url = None
        if post_image and post_image.filename:
            image_url = await upload_image_to_supabase(post_image, "community_images", "posts")
        
        # Create post data
        post_data = {
            "user_id": user_id,
            "user_name": user_name,
            "category": category,
            "message": message,
            "location": location
        }
        
        # Try to add image_url if we have one, but don't fail if column doesn't exist
        if image_url:
            try:
                post_data["image_url"] = image_url
                result = supabase.table("community_posts").insert(post_data).execute()
            except Exception as e:
                if "image_url" in str(e):
                    # Remove image_url and try again
                    del post_data["image_url"]
                    result = supabase.table("community_posts").insert(post_data).execute()
                    print(f"Warning: community_posts table doesn't have image_url column. Image uploaded but not linked: {image_url}")
                else:
                    raise e
        else:
            result = supabase.table("community_posts").insert(post_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create community post"
            )
        
        return {
            "message": "Community post created successfully", 
            "post_id": result.data[0]["id"],
            "image_uploaded": bool(image_url),
            "image_url": image_url if image_url else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create community post: {str(e)}"
        )

@app.get("/api/community")
async def get_community_posts():
    """Get all community posts"""
    try:
        result = supabase.table("community_posts").select("*").order("created_at", desc=True).limit(50).execute()
        return {"posts": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch community posts: {str(e)}"
        )

@app.get("/api/community/feed")
async def get_community_feed():
    """Get combined community posts and incident reports for the community feed"""
    try:
        # Get community posts
        community_result = supabase.table("community_posts").select("*").order("created_at", desc=True).limit(25).execute()
        community_posts = community_result.data or []
        
        # Get incidents and transform them to look like community posts
        incidents_result = supabase.table("incidents").select("*").order("created_at", desc=True).limit(25).execute()
        incidents = incidents_result.data or []
        
        # Transform incidents to community post format
        transformed_incidents = []
        for incident in incidents:
            transformed_incident = {
                "id": f"incident_{incident['id']}",
                "user_name": "Emergency Report",
                "category": "Alert",
                "message": f"🚨 {incident['incident_type']}: {incident['description']}",
                "location": incident["location"],
                "created_at": incident["created_at"],
                "post_type": "incident",
                "incident_type": incident["incident_type"],
                "status": incident.get("status", "reported"),
                "image_url": incident.get("photo_url")
            }
            transformed_incidents.append(transformed_incident)
        
        # Add post_type to regular community posts
        for post in community_posts:
            post["post_type"] = "community"
        
        # Combine and sort by creation date
        all_posts = community_posts + transformed_incidents
        all_posts.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"posts": all_posts, "count": len(all_posts)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch community feed: {str(e)}"
        )

@app.post("/api/sos")
async def create_sos_alert(
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_description: str = Form(...),
    emergency_type: str = Form("general"),
    user_name: str = Form(...),
    user_id: str = Form(...)
):
    """Create an SOS alert"""
    try:
        sos_data = {
            "user_id": user_id,
            "user_name": user_name,
            "latitude": latitude,
            "longitude": longitude,
            "location_description": location_description,
            "emergency_type": emergency_type,
            "status": "active"
        }
        
        result = supabase.table("sos_alerts").insert(sos_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create SOS alert"
            )
        
        return {"message": "SOS alert created successfully", "alert_id": result.data[0]["id"]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create SOS alert: {str(e)}"
        )

@app.get("/api/sos")
async def get_sos_alerts():
    """Get active SOS alerts"""
    try:
        result = supabase.table("sos_alerts").select("*").eq("status", "active").order("created_at", desc=True).execute()
        return {"alerts": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SOS alerts: {str(e)}"
        )

@app.post("/api/safe")
async def mark_safe(
    latitude: float = Form(...),
    longitude: float = Form(...),
    message: str = Form("User marked as safe"),
    user_name: str = Form(...),
    user_id: str = Form(...)
):
    """Mark user as safe"""
    try:
        safe_data = {
            "user_id": user_id,
            "user_name": user_name,
            "latitude": latitude,
            "longitude": longitude,
            "message": message
        }
        
        result = supabase.table("safe_status").insert(safe_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark as safe"
            )
        
        return {"message": "Marked as safe successfully", "safe_id": result.data[0]["id"]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as safe: {str(e)}"
        )

# Test database connection on startup
@app.on_event("startup")
async def startup_event():
    """Test database connection on startup"""
    try:
        # Test connection
        result = supabase.table("users").select("count").execute()
        print("✅ Successfully connected to Supabase database")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)