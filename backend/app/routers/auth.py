from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import hashlib

from ..core.database import get_db
from ..models.player import Player
from ..models.gm import InboxMessage
from ..schemas.common import (
    PlayerRegistrationCreate, 
    PlayerRegistrationRead, 
    PlayerLoginRequest, 
    PlayerLoginResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str) -> str:
    """Simple password hashing - in production, use proper hashing like bcrypt"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


@router.post("/register")
def register_player(payload: PlayerRegistrationCreate, db: Session = Depends(get_db)):
    """Register a new player account"""
    # Validate passwords match
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Check if username already exists
    existing_player = db.query(Player).filter(Player.name == payload.username).first()
    if existing_player:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Validate password strength (basic validation)
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    # Create new player account
    hashed_password = hash_password(payload.password)
    new_player = Player(
        name=payload.username,
        password_hash=hashed_password,
        is_approved=False  # Requires GM approval
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    
    # Create GM inbox message for account approval
    inbox_message = InboxMessage(
        type="account_registration", 
        payload={
            "username": payload.username,
            "registration_date": str(new_player.created_at),
            "player_id": new_player.id,
            "message": f"New player '{payload.username}' has requested an account"
        },
        player_id=new_player.id
    )
    
    db.add(inbox_message)
    db.commit()
    
    return {
        "success": True, 
        "message": "Registration successful! Your account is pending GM approval.",
        "player_id": new_player.id
    }


@router.post("/login", response_model=PlayerLoginResponse)
def login_player(payload: PlayerLoginRequest, db: Session = Depends(get_db)):
    """Authenticate player login"""
    # Find player by username
    player = db.query(Player).filter(Player.name == payload.username).first()
    
    if not player:
        return PlayerLoginResponse(
            success=False,
            message="Invalid username or password"
        )
    
    # Check if account has password (new system) or is legacy
    if player.password_hash:
        # New system - verify password
        if not verify_password(payload.password, player.password_hash):
            return PlayerLoginResponse(
                success=False,
                message="Invalid username or password"
            )
        
        # Check if account is approved
        if not player.is_approved:
            return PlayerLoginResponse(
                success=False,
                message="Your account is pending GM approval"
            )
    else:
        # Legacy system for existing players without passwords - always allow
        pass
    
    return PlayerLoginResponse(
        success=True,
        message="Login successful",
        player_id=player.id,
        username=player.name
    )


@router.get("/registration-requests", response_model=list[PlayerRegistrationRead])
def list_registration_requests(db: Session = Depends(get_db)):
    """Get all pending registration requests (for GM)"""
    return db.query(Player).filter(Player.is_approved == False, Player.password_hash.isnot(None)).all()


@router.post("/approve-registration/{player_id}")
def approve_registration(player_id: int, db: Session = Depends(get_db)):
    """Approve a player registration (GM only)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player.is_approved:
        raise HTTPException(status_code=400, detail="Player is already approved")
    
    # Approve the player
    player.is_approved = True
    from datetime import datetime
    player.approved_at = datetime.utcnow().isoformat()
    
    db.add(player)
    db.commit()
    
    return {"success": True, "message": f"Player '{player.name}' has been approved"}


@router.post("/reject-registration/{player_id}")
def reject_registration(player_id: int, db: Session = Depends(get_db)):
    """Reject a player registration (GM only)"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player.is_approved:
        raise HTTPException(status_code=400, detail="Cannot reject an approved player")
    
    # Delete the rejected player account
    db.delete(player)
    db.commit()
    
    return {"success": True, "message": f"Player registration for '{player.name}' has been rejected"}