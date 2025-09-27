from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.database import get_db
from ..models.gm import GMSettings, InboxMessage
from ..models.player import Player
from ..schemas.common import GMSettingsRead, GMSettingsUpdate, InboxMessageRead, GMPasswordChangeRequest
import hashlib

router = APIRouter(prefix="/gm", tags=["gm"])


def hash_password(password: str) -> str:
    """Simple password hashing - in production, use proper hashing like bcrypt"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def _get_or_create_settings(db: Session) -> GMSettings:
    settings = db.query(GMSettings).first()
    if not settings:
        settings = GMSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=GMSettingsRead)
def get_settings(db: Session = Depends(get_db)):
    settings = _get_or_create_settings(db)
    return settings


@router.patch("/settings", response_model=GMSettingsRead)
def update_settings(payload: GMSettingsUpdate, db: Session = Depends(get_db)):
    settings = _get_or_create_settings(db)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return settings
    for k, v in data.items():
        setattr(settings, k, v)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/inbox", response_model=list[InboxMessageRead])
def list_inbox(db: Session = Depends(get_db)):
    messages = db.query(InboxMessage).order_by(InboxMessage.created_at.desc()).all()
    # Convert to dict and add player_username
    result = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "type": message.type,
            "status": message.status,
            "payload": message.payload,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "player_id": message.player_id,
            "player_username": message.player.name if message.player else None
        }
        result.append(message_dict)
    return result


@router.get("/inbox/{message_id}", response_model=InboxMessageRead)
def get_inbox_message(message_id: int, db: Session = Depends(get_db)):
    message = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Convert to dict and add player_username
    return {
        "id": message.id,
        "type": message.type,
        "status": message.status,
        "payload": message.payload,
        "created_at": message.created_at,
        "updated_at": message.updated_at,
        "player_id": message.player_id,
        "player_username": message.player.name if message.player else None
    }


@router.patch("/inbox/{message_id}/status")
def update_message_status(
    message_id: int, 
    status: str, 
    response_data: dict | None = None,
    db: Session = Depends(get_db)
):
    message = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Update status
    message.status = status
    
    # Add response data to payload if provided
    if response_data:
        message.payload = {**message.payload, "response": response_data}
    
    db.commit()
    db.refresh(message)
    return {"success": True, "message": f"Message status updated to {status}"}


@router.post("/inbox")
def create_inbox_message(
    message_type: str,
    payload: dict,
    player_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Create a new inbox message (for players to submit requests)"""
    message = InboxMessage(
        type=message_type,
        payload=payload,
        player_id=player_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return {"success": True, "message_id": message.id}


@router.post("/approve-account/{message_id}")
def approve_account_registration(message_id: int, db: Session = Depends(get_db)):
    """GM approves a player account registration"""
    message = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.type != "account_registration":
        raise HTTPException(status_code=400, detail="Message is not an account registration")
    
    # Get the player from the message payload
    player_id = message.payload.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="No player ID found in message")
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Approve the player
    player.is_approved = True
    player.approved_at = datetime.utcnow().isoformat()
    
    # Update message status and add response
    message.status = "approved"
    message.payload = {
        **message.payload,
        "response": {
            "approved_by": "GM",
            "approved_at": datetime.utcnow().isoformat(),
            "message": "Account approved and activated"
        }
    }
    
    db.commit()
    
    return {"success": True, "message": f"Player '{player.name}' account has been approved"}


@router.post("/reject-account/{message_id}")
def reject_account_registration(message_id: int, db: Session = Depends(get_db)):
    """GM rejects a player account registration"""
    message = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.type != "account_registration":
        raise HTTPException(status_code=400, detail="Message is not an account registration")
    
    # Get the player from the message payload
    player_id = message.payload.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="No player ID found in message")
    
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Update message status and add response
    message.status = "rejected"
    message.payload = {
        **message.payload,
        "response": {
            "rejected_by": "GM",
            "rejected_at": datetime.utcnow().isoformat(),
            "message": "Account registration rejected"
        }
    }
    
    # Delete the player account
    db.delete(player)
    db.commit()
    
    return {"success": True, "message": f"Player '{player.name}' registration has been rejected"}


@router.post("/inbox/test-data")
def create_test_inbox_data(db: Session = Depends(get_db)):
    """Create sample inbox messages for testing"""
    # First, create test players if they don't exist
    test_players = [
        {"id": 1, "name": "Aragorn"},
        {"id": 2, "name": "Legolas"},
        {"id": 3, "name": "Gimli"}
    ]
    
    for player_data in test_players:
        existing_player = db.query(Player).filter(Player.id == player_data["id"]).first()
        if not existing_player:
            player = Player(id=player_data["id"], name=player_data["name"])
            db.add(player)
    
    db.commit()  # Commit players first
    
    test_messages = [
        {
            "type": "appraisal",
            "payload": {
                "item_type": "art",
                "item_name": "Ancient Vase",
                "description": "A mysterious ancient vase found in ruins",
                "estimated_value": "Unknown"
            },
            "player_id": 1
        },
        {
            "type": "business",
            "payload": {
                "business_name": "Dragon's Forge",
                "business_type": "Blacksmith",
                "investment_amount": "50.0",
                "description": "Expanding blacksmith operations with new equipment"
            },
            "player_id": 1
        },
        {
            "type": "investment",
            "payload": {
                "investment_name": "Mining Venture",
                "investment_type": "Resource Extraction",
                "investment_amount": "75.0",
                "description": "Partnership in local copper mine operation"
            },
            "player_id": 2
        },
        {
            "type": "loan",
            "payload": {
                "amount_requested": "100.0",
                "purpose": "Equipment upgrade",
                "proposed_interest": "5%",
                "repayment_plan": "10 sessions"
            },
            "player_id": 3
        }
    ]
    
    created_messages = []
    for test_msg in test_messages:
        message = InboxMessage(
            type=test_msg["type"],
            payload=test_msg["payload"],
            player_id=test_msg["player_id"]
        )
        db.add(message)
        created_messages.append(message)
    
    db.commit()
    
    return {"success": True, "messages_created": len(created_messages)}


@router.post("/change-password")
def change_gm_password(payload: GMPasswordChangeRequest, db: Session = Depends(get_db)):
    """Change GM password"""
    # Validate passwords match
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    # Find GM user
    gm_user = db.query(Player).filter(Player.name == "GM").first()
    if not gm_user:
        raise HTTPException(status_code=404, detail="GM user not found")
    
    # Verify current password if GM has a password set
    if gm_user.password_hash:
        if not verify_password(payload.current_password, gm_user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password strength
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")
    
    # Update password
    gm_user.password_hash = hash_password(payload.new_password)
    gm_user.is_approved = True  # Ensure GM is always approved
    
    db.add(gm_user)
    db.commit()
    
    return {"success": True, "message": "GM password updated successfully"}


@router.post("/initialize")
def initialize_gm_user(db: Session = Depends(get_db)):
    """Initialize GM user if it doesn't exist"""
    gm_user = db.query(Player).filter(Player.name == "GM").first()
    
    if not gm_user:
        # Create GM user with default password
        gm_user = Player(
            name="GM",
            password_hash=hash_password("gm123"),  # Default password
            is_approved=True
        )
        db.add(gm_user)
        db.commit()
        db.refresh(gm_user)
        return {"success": True, "message": "GM user created with default password 'gm123'"}
    else:
        # GM user exists, ensure it has the right properties
        if not gm_user.password_hash:
            gm_user.password_hash = hash_password("gm123")
        gm_user.is_approved = True
        db.add(gm_user)
        db.commit()
        return {"success": True, "message": "GM user already exists and has been updated"}
