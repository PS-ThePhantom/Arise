from datetime import date, datetime, timedelta
import pytz
import os
import re
from .slots import available_slots

def month_year_free_slot(month, year):

    # Validate month and year
    if not month:
        return "Missing 'month' query parameters"

    elif not year:
        return "Missing 'year' query parameters"

    try: 
        # Convert month/year to integers
        month = int(month)
        year = int(year)

        # Validate month and year ranges
        if month < 1 or month > 12:
            return "Invalid month: must be between 1 and 12"

        current_year = date.today().year
        next_year = current_year + 1
        if year < current_year or year > next_year:
            return f"Invalid year: must be between {current_year} and {next_year}"
        
        # Validate month/year is not in the past
        current_month = date.today().month
        if year == current_year and month < current_month:
            return "Invalid date: must be from the current month and year or later"

    # Catch conversion errors, non-integer inputs for month/year
    except (ValueError, TypeError):
        return "Invalid month or year"

    # If all validations pass, return None (no error)
    return None

def booking_data(data):
    # required fields and their length constraints
    required_fields = [{"name": "first_name", "min": 1, "max": 50, "title": True, "alpha": True},
                       {"name": "last_name", "min": 1, "max": 50, "title": True, "alpha": True},
                       {"name": "email", "min": 5, "max": 100, "lower": True},
                       {"name": "phone"},
                       {"name": "service", "min": 1, "max": 30, "lower": True, "values": ["tax", "accounting", "business consulting", "other"]},
                       {"name": "type", "min": 1, "max": 100, "lower": True, "values": ["personal", "business","both"]},
                       {"name": "date"},
                       {"name": "time"}
                      ]

    # check if reuired fields are valid
    for field in required_fields:
        error = check_field(data, field)

        if error:
            return error
        
    
    # conditionally required fields
    business_fields = [{"name": "company", "min": 1, "max": 100, "title": True},
                        {"name": "company_age", "min": 1, "max": 20},
                        {"name": "business_revenue", "min": 1, "max": 20}
                        ]
    
    if data['type'] in ['business', 'both']:
        for field in business_fields:
            error = check_field(data, field)

            if error:
                return error
    else:
        for field in business_fields:
            data[field['name']] = None

    #validate phone field
    data['phone'] = data['phone'].replace(" ", "")
    if data['phone'].startswith("0"):
        data['phone'] = "+27" + data['phone'][1:]
    elif data['phone'].startswith("27"):
        data['phone'] = "+" + data['phone']

    phone_regex = r'^\+27\d{9}$'
    if not bool(re.match(phone_regex, data['phone'])):
        return False, "Invalid phone number, must be South African format: +27XXXXXXXXX, 27XXXXXXXXX, or 0XXXXXXXXX"
    
    #validate email field
    email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
    if not bool(re.match(email_regex, data['email'])):
        return "Invalid email address"
    
    # validate date and time fields
    try:
        ZONE = pytz.timezone(os.getenv("TIMEZONE", "Africa/Johannesburg"))
        booking_dt = ZONE.localize(datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M"))

        if booking_dt < datetime.now(ZONE):
            return "Booking date and time must be in the future"
        elif booking_dt.date() > (date.today().replace(day=1) + timedelta(days=180)):
            return "Booking date must be within the next 6 months"
        
        # validate if booking time is available slot
        available_slots_list = available_slots(booking_dt.month, booking_dt.year, booking_dt.day)
        day_slots = next((item['slots'] for item in available_slots_list if item['day'] == booking_dt.day), [])
        if data['time'] not in day_slots:
            return f"Selected date and time is not available, please choose another slot, available slots for {data['date']} are: {', '.join(day_slots) if day_slots else 'none'}"
        
        # add booking datetime object to data
        data['datetime'] = booking_dt

    except:
        return "Invalid date or time format, date must be YYYY-MM-DD and time must be HH:MM in 24-hour format"

    # if all validations pass, return None (no error)
    return None

def check_field(data, requirements):
    name = requirements['name']
    min_length = requirements.get('min')
    max_length = requirements.get('max')
    values = requirements.get('values')
    title = requirements.get('title')
    lower = requirements.get('lower')
    alpha = requirements.get('alpha')

     # Validate field presence and type
    try:
        # Check if field is present and not empty
        if not data[name]:
            return f"provide a value for {name}"
        
        data[name] = str(data[name])  # attempt conversion to string

        # validate field contains only alphabetic characters if applicable
        if alpha and not data[name].isalpha():
            return f"{name} must contain only alphabetic characters"
        
        # validate field length if applicable
        if max_length and len(data[name]) > max_length:
            return f"{name} must be at most {max_length} characters long"
        elif min_length and len(data[name]) < min_length:
            return f"{name} must be at least {min_length} characters long"
        
        # format field if applicable
        if title:
            data[name] = data[name].title()
        elif lower:
            data[name] = data[name].lower()

        # check if field value is in allowed values if applicable
        if values and data[name] not in values:
            return f"Invalid {name}, must be one of: {', '.join(values)}"

    except TypeError:
        return f"Invalid data for '{name}' field, must be string or convertible to string"
    except KeyError:
        return f"Missing '{name}' field"

    return None