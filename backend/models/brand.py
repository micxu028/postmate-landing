import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy import Uuid
from models import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(String(50), nullable=False)    # yoga / fitness / pilates
    style = Column(String(50), nullable=False)        # professional / warm / energetic / minimalist
    tone = Column(String(50), nullable=False)          # professional / friendly / humorous / inspirational
    post_frequency = Column(Integer, default=7)       # 3, 5, or 7
    city = Column(String(100))
    state = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BrandImage(Base):
    __tablename__ = "brand_images"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(Uuid(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
