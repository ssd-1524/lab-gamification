from fastapi import APIRouter
from app.utils.auth import supabase

router = APIRouter(prefix="/locations", tags=["Lookups"])

# app/routers/location.py
@router.get("/")
def get_locations():
    # MUST match exactly what is in your Supabase 'Table Editor'
    response = supabase.table("location").select("loc_id, loc_name").execute()
    
    # DEBUG: Print this to your FastAPI terminal to see errors
    if hasattr(response, 'error') and response.error:
        print(f"SUPABASE ERROR: {response.error}")
        
    return response.data