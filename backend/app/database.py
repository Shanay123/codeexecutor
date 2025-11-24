from supabase import create_client, Client
from app.config import settings

print(f"[DATABASE INIT] Creating Supabase client")
print(f"[DATABASE INIT] URL: {settings.supabase_url}")
print(f"[DATABASE INIT] Service key (first 20 chars): {settings.supabase_service_key[:20]}...")
print(f"[DATABASE INIT] Anon key (first 20 chars): {settings.supabase_anon_key[:20]}...")

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_client() -> Client:
    return supabase
