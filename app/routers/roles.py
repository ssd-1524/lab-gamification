from fastapi import APIRouter
from app.utils.auth import supabase

router = APIRouter(prefix="/roles", tags=["Lookups"])

@router.get("/")
def get_roles():
    # Uses HTTPS (443) - much more stable than SQLAlchemy for cloud lookups
    response = supabase.table("role").select("role_id, role_name").execute()
    # DEBUG: Print this to your FastAPI terminal to see errors
    if hasattr(response, 'error') and response.error:
        print(f"SUPABASE ERROR: {response.error}")
    return response.data # supabase-py returns a list of dicts directly