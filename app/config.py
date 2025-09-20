import secrets
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# JWT Settings
SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Supabase Settings
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")