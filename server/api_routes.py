from flask import Blueprint, jsonify, request
from .services.data_validity import month_year_free_slot, booking_data
from .services.slots import available_slots
from .services.book import create_booking
from .services.email import create_email
from .services.db.crud import unsubscribe_client, check_client_subscribed

api_routes = Blueprint('api', __name__)

@api_routes.route("/unsubscribe")
def unsubscribe():
    token = request.args.get("token")
    
    if not token:
        return jsonify({"error": "Missing unsubscribe token."}), 400
    
    error = unsubscribe_client(token)
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify({"message": "You have been unsubscribed successfully."}), 200

@api_routes.route("/free-slots")
def get_slots():
    month  = request.args.get("month")
    year = request.args.get("year")
    error = month_year_free_slot(month, year)

    if error:
        return jsonify({"error": error}), 400
    
    month = int(month)
    year = int(year)
    slots = available_slots(month, year)

    return jsonify({"year": year, "month": month, "slots": slots}), 200

@api_routes.route("/book", methods=["POST"])
def book():
    data = request.get_json()
    error = booking_data(data)

    #test data
    if error:
        return jsonify({"error": error}), 400
    
    # If all validations pass, proceed with booking logic (e.g., save to database, send confirmation email, etc.)
    error, meet_link = create_booking(data)
    if error:
        return jsonify({"error": error}), 500
    
    # If booking is successful, send email to the client
    formatted_date = data['datetime'].strftime("%B %d, %Y")
    formatted_time = data['datetime'].strftime("%I:%M %p")

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

    error = create_email(client_email, email_subject, email_message)
    if error:
        return jsonify({"error": error}), 500

    # If email is sent successfully, send email attachment to the client if subscribed
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

        error = create_email(client_email, attachment_subject, attachment_message, attachments)
        if error:
            return jsonify({"error": error}), 500
    
    # return success response to client
    return jsonify({"message": "Booking successful"}), 200

@api_routes.route("/<path:invalid_path>")
def api_not_found(invalid_path):
    return jsonify({
        "error": "Invalid API endpoint",
        "path": f"/api/{invalid_path}"
    }), 404