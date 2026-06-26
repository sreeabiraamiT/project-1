from database import Base
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    consumer_number = Column(String(12), primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    bills = relationship("Bill", back_populates="user")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    consumer_number = Column(
        String(12),
        ForeignKey("users.consumer_number")
    )
    region=Column(String(50))
    bill_month = Column(Date)
    tariff_category = Column(String)
    units_consumed = Column(Float)
    amount_due = Column(Float)
    uploaded_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="bills")
    analysis = relationship("Analysis", back_populates="bill")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    ai_summary = Column(Text)
    saving_tips = Column(JSONB)
    analyzed_at = Column(DateTime, server_default=func.now())

    bill = relationship("Bill", back_populates="analysis")
