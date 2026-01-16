from .db.crud import add_client, add_booking
from .calendar import create_event

def create_booking(data):
    # add client if not existing and get client_id
    client = {
        "email": data['email'],
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "phone": data['phone']
    }

    # add or update client in the database
    result = add_client(client)
    if result["error"]:
        return {"error": result["error"], "meeting_link": None}

    # create a new booking event calendar
    booking = {
        "datetime": data['datetime'],
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "phone": data['phone'],
        "email": data['email'],
        "service": data['service'],
        "type": data['type'],
        "company": data.get('company'),
        "company_age": data.get('company_age'),
        "business_revenue": data.get('business_revenue'),
        "additional_info": data.get('additional_info')
    }

    event = create_event(booking)
    if event["error"]:
        return event

    # Save the booking information to the database
    booking['client_id'] = result["client_id"]
    booking['meeting_link'] = event["meeting_link"]

    error = add_booking(booking)
    return {"error": error, "meeting_link": event["meeting_link"]}