from .config import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, DateTime, Text
from sqlalchemy.sql import func
import uuid
from datetime import datetime

class Client(Base):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    unsubscribe_token = Column(String, unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    subscribed = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("length(email) >= 5", name="min_email_length"),
        CheckConstraint("length(email) <= 50", name="max_email_length"),
        CheckConstraint("length(first_name) >= 1", name="min_first_name_length"),
        CheckConstraint("length(first_name) <= 50", name="max_first_name_length"),
        CheckConstraint("length(last_name) >= 1", name="min_last_name_length"),
        CheckConstraint("length(last_name) <= 50", name="max_last_name_length"),
        CheckConstraint("length(phone) = 12", name="phone_size"),
    )


class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    service = Column(String, nullable=False)
    type = Column(String, nullable=False)
    company = Column(String, nullable=True)
    company_age = Column(String, nullable=True)
    business_revenue = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    additional_info = Column(String, nullable=True)
    meet_link = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("length(service) >= 1", name="min_service_length"),
        CheckConstraint("length(service) <= 30", name="max_service_length"),
        CheckConstraint("service IN ('tax', 'accounting', 'business consulting', 'other')", name="valid_service"),
        CheckConstraint("length(type) >= 1", name="min_type_length"),
        CheckConstraint("length(type) <= 100", name="max_type_length"),
        CheckConstraint("type IN ('personal', 'business', 'both')", name="valid_type"),
        CheckConstraint("date >= NOW()", name="valid_date"),
        CheckConstraint("length(company) >= 1", name="min_company_length"),
        CheckConstraint("length(company) <= 100", name="max_company_length"),
        CheckConstraint("length(company_age) >= 1", name="min_company_age_length"),
        CheckConstraint("length(company_age) <= 20", name="max_company_age_length"),
        CheckConstraint("length(business_revenue) >= 1", name="min_business_revenue_length"),
        CheckConstraint("length(business_revenue) <= 20", name="max_business_revenue_length"),
    )

class Error(Base):
    __tablename__ = "errors"
    error_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    message = Column(String, nullable=False)
    stack_trace = Column(Text, nullable=True)