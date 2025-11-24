from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

# For user-authenticated requests, we'll use the anon key with JWT
def get_supabase_client() -> Client:
    return supabase

