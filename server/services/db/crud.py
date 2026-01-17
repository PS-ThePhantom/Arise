from email.mime import message
from .config import SessionLocal
from .models import Client, Booking, Error
import traceback, logging

#file logging setup
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
fh = logging.FileHandler("error.log")
fh.setLevel(logging.ERROR)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
fh.setFormatter(formatter)

error_logger.addHandler(fh)

def check_client_subscribed(email):
    db = None

    # try to connect to db
    try:
        db = SessionLocal()
        
        client = db.query(Client).filter(Client.email == email).first()
        subscribed  = False
        
        if client:
            subscribed = client.subscribed

        return {"subscribed": subscribed, "error": None}

    except Exception as e:
        error_log(str(e), traceback.format_exc())
        return {"subscribed": False, "error": "Something went wrong. Please try again later."}
    
    finally:
        if db:
            db.close()

def unsubscribe_client(token):
    db = None

    # try to connect to db
    try:
        db = SessionLocal()
        
        client = db.query(Client).filter(Client.unsubscribe_token == token).first()
        if not client:
            return {"error": "Invalid unsubscribe token.", "code": 400}

        client.subscribed = False
        db.commit()

        return {"error": None}
    
    except Exception as e:
        error_log(str(e), traceback.format_exc())
        if db:
            db.rollback()

        return {"error": "Something went wrong. Please try again later.", "code": 500}
    
    finally:
        if db:
            db.close()

def add_client(client_details):
    db = None    

    # try to connect to db
    try:
        db = SessionLocal()
       
        client = Client(
            email=client_details['email'],
            first_name=client_details['first_name'],
            last_name=client_details['last_name'],
            phone=client_details['phone']
        )

        existing_client = db.query(Client).filter(Client.email == client.email).first()
        if existing_client:
            # update existing client details
            existing_client.first_name = client.first_name
            existing_client.last_name = client.last_name
            existing_client.phone = client.phone
            db.commit()
            db.refresh(existing_client)
            client_id = existing_client.client_id

        else:
            # add new client
            db.add(client)
            db.commit()
            db.refresh(client)
            client_id = client.client_id

        return {"error": None, "client_id": client_id}

    except Exception as e:
        error_log(str(e), traceback.format_exc())
        if db:
            db.rollback()

        return {"error": "server error. Please try again later.", "client_id": None}
    
    finally:
        if db:
            db.close()
    
def add_booking(booking_details):
    db = None

    try:
        db = SessionLocal()
        
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

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return {"error": None}

    except Exception as e:
        if db:
            db.rollback()

        error_log(str(e), traceback.format_exc())
        return {"error": "Something went wrong. Please try again later."}
    
    finally:
        if db:
            db.close()
    
def error_log(message, stack_trace=None):
    db = None
    
    try:
        db = SessionLocal()
        error = Error(message=message, stack_trace=stack_trace)
        db.add(error)
        db.commit()
    
    except Exception as e:
        if db:
            db.rollback()

        error_logger.exception("Failed to log error to database: ")
        error_logger.error("Original error:\n%s\n%s", message, stack_trace or "")

    finally:
        if db:
            db.close()