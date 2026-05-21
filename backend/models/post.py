import uuid
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text, func
from sqlalchemy import Uuid
from models import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(Uuid(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    day_of_week = Column(Integer, nullable=False)    # 0=Mon .. 6=Sun
    caption = Column(String(2000), nullable=False)
    hashtags = Column(Text, default="[]")            # JSON array string; ARRAY in production
    image_url = Column(String(500))
    status = Column(String(20), default="pending")   # pending / approved / rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
