from ... import db
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
import uuid

class Client(db.Model):
    __tablename__ = "clients"

    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    unsubscribe_token = db.Column(
        db.String(64),
        unique=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    subscribed = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("length(email) >= 5", name="min_email_length"),
        CheckConstraint("length(email) <= 50", name="max_email_length"),
        CheckConstraint("length(first_name) >= 1", name="min_first_name_length"),
        CheckConstraint("length(first_name) <= 50", name="max_first_name_length"),
        CheckConstraint("length(last_name) >= 1", name="min_last_name_length"),
        CheckConstraint("length(last_name) <= 50", name="max_last_name_length"),
        CheckConstraint("length(phone) = 12", name="phone_size"),
    )


class Booking(db.Model):
    __tablename__ = "bookings"

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.client_id", ondelete="CASCADE"),
        nullable=False
    )
    service = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    company_age = db.Column(db.String(20), nullable=True)
    business_revenue = db.Column(db.String(20), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    additional_info = db.Column(db.String, nullable=True)
    meet_link = db.Column(db.String, nullable=True)

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


class Error(db.Model):
    __tablename__ = "errors"

    error_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=func.now())
    message = db.Column(db.String, nullable=False)
    stack_trace = db.Column(db.Text, nullable=True)
