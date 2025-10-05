
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,String,Boolean,Text,DateTime,func

Base=declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer,primary_key=True)
    username = Column(String,nullable=False,unique=True)
    first_name=Column(String,nullable=True)
    last_name=Column(String,nullable=True)
    mobile_number= Column(String,nullable=True)
    is_mobile_number_verified=Column(Boolean,nullable=True)
    email_address=Column(String,nullable=True)
    is_email_address_verified=Column(Boolean,nullable=True)
    totp_secret_encrypted = Column(Text, nullable=True)
    is_totp_verified=Column(Boolean,nullable=True)
    created_at=Column(DateTime, default=func.now())
    updated_at=Column(DateTime, default=func.now(), onupdate=func.now())