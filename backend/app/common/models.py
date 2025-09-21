# Make sure models.py doesn't import from auth.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_by = Column(String)  # Track who created the account
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email_histories = relationship("EmailHistory", back_populates="user")
    email_name_maps = relationship("EmailNameMap", back_populates="user")

class EmailHistory(Base):
    __tablename__ = "email_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipient = Column(String)
    subject = Column(String)
    content_preview = Column(String)
    full_content_html = Column(String)
    email_id = Column(String)
    status = Column(String, default="sent")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="email_histories")

class EmailNameMap(Base):
    __tablename__ = "email_name_maps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    email_address = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="email_name_maps")