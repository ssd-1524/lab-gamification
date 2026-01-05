from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.routers.deps import get_db
from app.models import schema
from app.utils.auth import supabase
from pydantic import BaseModel, EmailStr
from app.routers.deps import get_authenticated_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Request Schemas ---
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_id: UUID
    loc_id: UUID

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Endpoints ---

@router.post("/signup/")
async def signup(payload: UserSignup, db: Session = Depends(get_db)):
    auth_user_id = None
    try:
        # 1. Create User in Supabase Auth
        auth_res = supabase.auth.sign_up({
            "email": payload.email, 
            "password": payload.password
        })
        
        if not auth_res.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create user in identity provider."
            )
        
        auth_user_id = auth_res.user.id
        user_uuid = UUID(auth_user_id)

        # 2. Create Local User Profile
        new_user = schema.Users(
            user_id=user_uuid,
            name=payload.name,
            role_id=payload.role_id,
            loc_id=payload.loc_id
        )
        db.add(new_user)
        
        # Flush pushes 'new_user' to DB so the Wallet FK check passes
        db.flush() 

        # 3. Create Point Wallet for the user
        new_wallet = schema.PointWallet(
            user_id=user_uuid,
            total_points=0,
            rank="Bronze"
        )
        db.add(new_wallet)

        db.commit()
        return {"status": "success", "user_id": str(user_uuid)}

    except Exception as e:
        db.rollback()
        # Clean up Supabase if the local DB failed to prevent duplicate email errors later
        if auth_user_id:
            try:
                supabase.auth.admin.delete_user(auth_user_id)
            except:
                pass # Silent fail if admin delete isn't configured
        
        print(f"CRITICAL SIGNUP ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database error: {str(e)}"
        )

@router.post("/login/")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        # 1. Authenticate with Supabase
        auth_res = supabase.auth.sign_in_with_password({
            "email": payload.email, 
            "password": payload.password
        })

        if not auth_res.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = auth_res.user.id

        # 2. Fetch full profile from local DB (including role and location names)
        user_profile = db.query(
            schema.Users.name,
            schema.Users.role_id,
            schema.Users.loc_id,
            schema.Role.role_name,
            schema.Location.loc_name
        ).join(schema.Role, schema.Users.role_id == schema.Role.role_id)\
         .join(schema.Location, schema.Users.loc_id == schema.Location.loc_id)\
         .filter(schema.Users.user_id == user_id).first()

        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found in local database")

        # 3. Return combined data for Streamlit session state
        return {
            "access_token": auth_res.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user_id),
                "name": user_profile.name,
                "role_id": str(user_profile.role_id),
                "loc_id": str(user_profile.loc_id),
                "role_name": user_profile.role_name,
                "loc_name": user_profile.loc_name
            }
        }

    except Exception as e:
        print(f"LOGIN ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
@router.get("/points")
def get_my_points(
    user: dict = Depends(get_authenticated_user),
    db: Session = Depends(get_db),
):
    """
    Return total points and rank for the authenticated user
    """
    user_id = user["sub"]

    wallet = (
        db.query(schema.PointWallet)
        .filter(schema.PointWallet.user_id == user_id)
        .first()
    )

    return {
        "total_points": wallet.total_points if wallet else 0,
        "rank": wallet.rank if wallet else None,
    }
