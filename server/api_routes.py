import os
from flask import Blueprint, jsonify, request
from .services.data_validity import month_year_free_slot, booking_data
from .services.slots import available_slots
from .services.book import create_booking
from .services.email import create_email, send_emails
from .services.db.crud import unsubscribe_client, check_client_subscribed, error_log
from datetime import date, timedelta
import threading

api_routes = Blueprint('api', __name__)

@api_routes.route("/unsubscribe")
def unsubscribe():
    token = request.args.get("token")
    
    if not token:
        return jsonify({"error": "Missing unsubscribe token."}), 400
    
    result = unsubscribe_client(token)
    if result["error"]:
        return jsonify({"error": result["error"]}), result["code"]
    
    return jsonify({"message": "You have been unsubscribed successfully."}), 200

@api_routes.route("/last-possible-booking-date")
def get_max_possible_booking_date():
    max_days = os.getenv("MAX_DAYS_AHEAD", None)

    if (not max_days): 
        return jsonify({"limit": False}), 200
    
    maxDate = date.today().replace(day=1) + timedelta(days=int(max_days))
    return jsonify({"limit": True,
                    "max_booking_date": maxDate.strftime("%Y-%m"),
                    "month": maxDate.month,
                    "year": maxDate.year}), 200

@api_routes.route("/free-slots")
def get_slots():
    month  = request.args.get("month")
    year = request.args.get("year")
    error = month_year_free_slot(month, year)

    if error:
        return jsonify({"error": error}), 400
    
    month = int(month)
    year = int(year)
    result = available_slots(month, year)
    if result["error"]:
        return jsonify({"error": result["error"]}), 400

    slots = result["slots"]

    return jsonify({"year": year, "month": month, "slots": slots}), 200

def background_booking(data):
    result = create_booking(data)
    if result["error"]:
        error_log(f"Booking failed for {data['email']}: {result['error']}")
        return
    meet_link = result["meeting_link"]
    
    # If booking is successful, send email to the client
    formatted_date = data['datetime'].strftime("%B %d, %Y")
    formatted_time = data['datetime'].strftime("%I:%M %p")
    mails = []

    client_email = data['email']
    email_subject = f"Hey {data['first_name']}! your session with Arise Consulting has been confirmed"
    email_message = (
        f" Hey {data['first_name']}!\n\n"
        f"Thank you for showing interest in Arise Consulting.\n\n"
        f"Your appointment has been confirmed for {formatted_date} at {formatted_time}.\n"
        f"When it is time, please join using this Meeting ID: {meet_link}\n\n"
        f"Best regards,\n"
        f"Murangi Makhesha\n"
        f"Accounting and Tax Specialist\n"
    )

    mails.append(create_email(client_email, email_subject, email_message))
    subscribed, error = check_client_subscribed(client_email)

    if subscribed:
        attachment_subject = f"Hey {data['first_name']}! your free Tax Season Checklist"
        attachment_message = (
            f" Hey {data['first_name']}!\n\n"
            f"Thank you for booking your free strategy session with us.\n\n"
            f"Attached is your free Tax Season Checklist pdf as promised.\n\n"
            f"Best regards,\n"
            f"Murangi Makhesha\n"
            f"Accounting and Tax Specialist\n"
        )
        attachments = [
            {
                "file": "static/files/checklist.pdf",
                "name": f"Arise Consulting Tax Season Checklist for {data['first_name']}.pdf"
            }
        ]
        mails.append(create_email(client_email, attachment_subject, attachment_message, attachments))
    
    error = send_emails(mails)
    if error:
        error_log(f"Failed to send emails for {data['email']}: {error}")
        return

@api_routes.route("/book", methods=["POST"])
def book():
    data = request.get_json() # Debugging statement
    error = booking_data(data)

    #test data
    if error:
        return jsonify({"error": error}), 400
    
    threading.Thread(target=background_booking, args=(data,)).start()
    return jsonify({"message": "Booking received, processing…"}), 202

@api_routes.route("/<path:invalid_path>")
def api_not_found(invalid_path):
    return jsonify({
        "error": "Invalid API endpoint",
        "path": f"/api/{invalid_path}"
    }), 404