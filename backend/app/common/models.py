from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) 
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)  # For deactivating accounts
    is_admin = Column(Boolean, default=False)
    created_by = Column(String)  # Track who created the account
    created_at = Column(DateTime, default=datetime.utcnow)


class RegistrationRequest(Base):
    __tablename__ = "registration_requests"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    reason = Column(String)
    requested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, approved, rejected


class EmailHistory(Base):
    __tablename__ = "email_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content_preview = Column(Text)
    full_content_html = Column(Text, nullable=True)
    email_id = Column(String)  # External email service ID
    status = Column(String, default="sent")  # sent, failed, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to user
    user = relationship("User")

class EmailNameMap(Base):
    __tablename__ = "email_name_maps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    email_address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to user
    user = relationship("User")