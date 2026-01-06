from supabase import create_client
from app.config import get_settings

settings = get_settings()

supabase_client = create_client(
    settings.SUPABASE_URL,
    # Use service role key for backend jobs if available
    settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
)
