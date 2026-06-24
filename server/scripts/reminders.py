from datetime import datetime, timedelta
from ..services.db.crud import get_bookings_for_reminders, update_reminders_sent
from ..services.email import create_email, send_emails

def sendReminders():
    # Function to send reminders to users
    mails = []
    now_time = datetime.now()
    one_hour_later = now_time + timedelta(hours=1)
    twenty_four_hours_later = now_time + timedelta(hours=24)
    mins_range = 5
    secs_range = mins_range * 60

    #bookings within the 24-hour window ±5 minutes
    bookings_24hr = get_bookings_for_reminders(twenty_four_hours_later - timedelta(seconds=secs_range), twenty_four_hours_later + timedelta(seconds=secs_range))
    bookings_1hr = get_bookings_for_reminders(one_hour_later - timedelta(seconds=secs_range), one_hour_later + timedelta(seconds=secs_range))
    bookings_now = get_bookings_for_reminders(now_time - timedelta(seconds=secs_range), now_time + timedelta(seconds=secs_range))
    

    for booking in bookings_24hr:
        remindersSent = booking.reminders_sent.split(',') if booking.reminders_sent else []
        if '24hr' in remindersSent:
            continue  # Skip sending the 24-hour reminder if it has already been sent
        
        # Send 24-hour reminder email
        subject = f"Hey! {booking.first_name}, Your Free Consultation is in 24 Hours!"
        body = f'''Hey {booking.first_name}

This is Murangi from Arise Consulting
Just a friendly reminder that your free consultation is in 24 Hours: {booking.strftime('%Y-%m-%d')} at {booking.date.strftime('%H:%M')}

When it is time, please use this Meeting ID {booking.meet_link}

Best regards,
Murangi Makhesha
Accounting and Tax Specialist

If you no longer wish to receive these emails you may unsubscribe by clicking the link below:
https://ariseconsulting.co.za/unsubscribe?token={booking.unsubscribe_token}'''
        
        mails.append(create_email(booking.email, subject, body))
        update_reminders_sent(booking.booking_id, '24hr')  # Update the reminders_sent field to include '24hr'

        
    for booking in bookings_1hr:
        # Send 1-hour reminder email
        remindersSent = booking.reminders_sent.split(',') if booking.reminders_sent else []
        if '1hr' in remindersSent:
            continue  # Skip sending the 1-hour reminder if it has already been sent
        subject = f"Hey! {booking.first_name}, Your Free Consultation is in 1 Hour!"
        body = f'''Hey {booking.first_name}

This is Murangi from Arise Consulting. I'm super excited to talk with you.
Just a friendly reminder that your free consultation is in 1 Hour: {booking.strftime('%Y-%m-%d')} at {booking.date.strftime('%H:%M')}

When it is time, please use this Meeting ID {booking.meet_link}

Best regards,
Murangi Makhesha
Accounting and Tax Specialist

If you no longer wish to receive these emails you may unsubscribe by clicking the link below:
https://ariseconsulting.co.za/unsubscribe?token={booking.unsubscribe_token}'''
        
        mails.append(create_email(booking.email, subject, body))
        update_reminders_sent(booking.booking_id, '1hr')  # Update the reminders_sent field to include '1hr'

    for booking in bookings_now:
        # Send now reminder email
        remindersSent = booking.reminders_sent.split(',') if booking.reminders_sent else []
        if 'now' in remindersSent:
            continue  # Skip sending the "now" reminder if it has already been sent
        subject = f"Hey! {booking.first_name}, Your appointment is starting now!"
        body = f'''Hey {booking.first_name}

Hi {booking.first_name},
Our appointment is about to start. Please join here: {booking.meet_link}'''
        
        mails.append(create_email(booking.email, subject, body))
        update_reminders_sent(booking.booking_id, 'now')  # Update the reminders_sent field to include 'now'

    send_emails(mails)

sendReminders()