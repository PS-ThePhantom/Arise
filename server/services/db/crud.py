from .config import SessionLocal
from .models import Client, Booking, Error
import logging, traceback

logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def check_client_subscribed(email):
    # try to connect to db
    try:
        db = SessionLocal()
    except Exception as connect_error:
        logging.error("Database connection failed:\n%s", traceback.format_exc())
        return False, "server error. Please try again later."

    try:
        client = db.query(Client).filter(Client.email == email).first()
        if not client:
            return False, None

        return client.subscribed, None
    
    except Exception as e:
        try:
            error = Error(
                message=str(e),
                stack_trace=traceback.format_exc()
            )

            db.add(error)
            db.commit()

        except Exception as log_error:
            logging.error("Failed to log error to database:\n%s", traceback.format_exc())

        return False, "Something went wrong. Please try again later."

def unsubscribe_client(token):
    # try to connect to db
    try:
        db = SessionLocal()
    except Exception as connect_error:
        logging.error("Database connection failed:\n%s", traceback.format_exc())
        return "server error. Please try again later."

    try:
        client = db.query(Client).filter(Client.unsubscribe_token == token).first()
        if not client:
            return "Invalid unsubscribe token."

        client.subscribed = False
        db.commit()

        return None
    
    except Exception as e:
        db.rollback()
        
        try:
            error = Error(
                message=str(e),
                stack_trace=traceback.format_exc()
            )

            db.add(error)
            db.commit()

        except Exception as log_error:
            logging.error("Failed to log error to database:\n%s", traceback.format_exc())

        return "Something went wrong. Please try again later."

def add_client(client_details):
    client = Client(
        email=client_details['email'],
        first_name=client_details['first_name'],
        last_name=client_details['last_name'],
        phone=client_details['phone']
    )

    # try to connect to db
    try:
        db = SessionLocal()
    except Exception as connect_error:
        logging.error("Database connection failed:\n%s", traceback.format_exc())
        return "server error. Please try again later.", None

    try:
        existing_client = db.query(Client).filter(Client.email == client.email).first()
        if existing_client:
            # update existing client details
            existing_client.first_name = client.first_name
            existing_client.last_name = client.last_name
            existing_client.phone = client.phone
            db.commit()
            db.refresh(existing_client)

            return None, existing_client.client_id

        db.add(client)
        db.commit()
        db.refresh(client)

        return None, client.client_id
    
    except Exception as e:
        db.rollback()
        
        try:
            error = Error(
                message=str(e),
                stack_trace=traceback.format_exc()
            )

            db.add(error)
            db.commit()

        except Exception as log_error:
            logging.error("Failed to log error to database:\n%s", traceback.format_exc())

        return "Something went wrong. Please try again later.", None
    
def add_booking(booking_details):
    booking = Booking(
        client_id=booking_details['client_id'],
        service=booking_details['service'],
        type=booking_details['type'],
        company=booking_details.get('company'),
        company_age=booking_details.get('company_age'),
        business_revenue=booking_details.get('business_revenue'),
        date=booking_details['datetime'],
        additional_info=booking_details.get('additional_info'),
        meet_link=booking_details.get('meeting_link')
    )

    # try to connect to db
    try:
        db = SessionLocal()
    except Exception as connect_error:
        logging.error("Database connection failed:\n%s", traceback.format_exc())
        return "server error. Please try again later."

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)

        return None
    
    except Exception as e:
        db.rollback()
        
        try:
            error = Error(
                message=str(e),
                stack_trace=traceback.format_exc()
            )

            db.add(error)
            db.commit()

        except Exception as log_error:
            logging.error("Failed to log error to database:\n%s", traceback.format_exc())

        return "Something went wrong. Please try again later."