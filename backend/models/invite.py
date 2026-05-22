import uuid
import secrets
import string
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, func
from sqlalchemy import Uuid
from models import Base


def generate_invite_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "PM" + "".join(secrets.choice(alphabet) for _ in range(length))


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True, default=generate_invite_code)
    email = Column(String(255), nullable=True)
    used_by_user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    max_uses = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
