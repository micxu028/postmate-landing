from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.invite import Invite, generate_invite_code
from services.auth_service import get_current_user
from services.email_service import send_email, build_invite_email

router = APIRouter(prefix="/api/invites", tags=["invites"])


class CreateInviteRequest(BaseModel):
    email: Optional[EmailStr] = None
    count: int = 1


class CreateInviteResponse(BaseModel):
    codes: list[str]


class ValidateInviteResponse(BaseModel):
    valid: bool
    email: Optional[str] = None


@router.post("", response_model=CreateInviteResponse)
async def create_invites(
    req: CreateInviteRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    codes = []
    for _ in range(req.count):
        invite = Invite(email=req.email, code=generate_invite_code())
        db.add(invite)
        codes.append(invite.code)
    await db.commit()

    # Send invite email if email was provided
    if req.email and codes:
        invite_link = f"https://postmate.net/app/invite.html?code={codes[0]}"
        html = build_invite_email(invite_link)
        await send_email(to=req.email, subject="You're invited to PostMate Beta!", html=html)

    return CreateInviteResponse(codes=codes)


@router.get("/validate/{code}", response_model=ValidateInviteResponse)
async def validate_invite(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invite).where(Invite.code == code))
    invite = result.scalar_one_or_none()
    if not invite:
        return ValidateInviteResponse(valid=False)
    if invite.used_by_user_id is not None and invite.max_uses == 1:
        return ValidateInviteResponse(valid=False)
    return ValidateInviteResponse(valid=True, email=invite.email)


@router.get("")
async def list_invites(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Invite).order_by(Invite.created_at.desc()))
    invites = result.scalars().all()
    return [
        {
            "code": i.code,
            "email": i.email,
            "used": i.used_by_user_id is not None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in invites
    ]
