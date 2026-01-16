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

    error_message, client_id = add_client(client)
    if error_message:
        return error_message
    
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

    error_message, meeting_link = create_event(booking)
    if error_message:
        return error_message, None

    # Save the booking information to the database
    booking['client_id'] = client_id
    booking['meeting_link'] = meeting_link

    error = add_booking(booking)
    return error, meeting_link