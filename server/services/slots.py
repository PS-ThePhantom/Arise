from datetime import timedelta, datetime
import pytz
from .calendar import get_normal_events as get_events, get_holiday_events as get_holidays
import os

def available_slots(month, year, specific_day=None):
    slots = []
    booking_minutes = int(os.getenv("BOOKING_MINUTES", "30"))

    #first and last day of the given month
    time_zone = pytz.timezone("Africa/Johannesburg")
    first_day = time_zone.localize(datetime(year, month, 1))
    next_month_first_day = time_zone.localize(datetime(year, month + 1, 1)) if month < 12 else time_zone.localize(datetime(year + 1, 1, 1))
    last_day = next_month_first_day - timedelta(seconds=1)
    today = datetime.now(time_zone)

    #get all the events of the month from the calendar
    start_dt = first_day if first_day > today else today
    events_info = get_events(start_dt, last_day)

    if events_info["error"]:
        return {"error": events_info["error"], "slots": slots}

    events = events_info["events"]
    holidays = {}
    if os.getenv("CALENDAR_HOLIDAYS_ID") and os.getenv("TIME_HOLIDAYS"):
        holidays_info = get_holidays(first_day, last_day)

        if holidays_info["error"]:
            return {"error": holidays_info["error"], "slots": slots}
        
        holidays = holidays_info["events"]

    #iterate through each day of the month
    days = [specific_day] if specific_day else range(first_day.day, last_day.day + 1)

    for day in days:
        date = time_zone.localize(datetime(year, month, day))
        
        #if the day is in the past or a non working day, skip it
        #if its a working day, get the working hours
        if date.date() < today.date():
            slots.append({"day": day, "slots": []})
            continue

        #check if the day is a holiday and if it spans multiple days
        # ie calendar event for holiday ends on 00:00 next day instead of 23:59 same day
        # ignore the second day in that case as its not a holiday
        elif holidays.get(day) and (holidays[day][0][1] == holidays[day][0][0] or day != holidays[day][0][1].day):
            if not os.getenv("TIME_HOLIDAYS"):
                slots.append({"day": day, "slots": []})
                continue
            
            work_start_str, work_end_str = os.getenv("TIME_HOLIDAYS").split("-")

        # if not a holiday, check if its a weekday or weekend and get working hours if set
        elif date.weekday() < 5:
            if not os.getenv("TIME_WEEKDAYS"):
                slots.append({"day": day, "slots": []})
                continue

            work_start_str, work_end_str = os.getenv("TIME_WEEKDAYS").split("-")

        elif date.weekday() == 5:
            if not os.getenv("TIME_SATURDAYS"):
                slots.append({"day": day, "slots": []})
                continue

            work_start_str, work_end_str = os.getenv("TIME_SATURDAYS").split("-")

        elif date.weekday() == 6:
            if not os.getenv("TIME_SUNDAYS"):
                slots.append({"day": day, "slots": []})
                continue
            
            work_start_str, work_end_str = os.getenv("TIME_SUNDAYS").split("-")

        #turn work time string to datetime
        work_start = datetime.strptime(work_start_str, "%H:%M")
        work_end = datetime.strptime(work_end_str, "%H:%M")        

        # if day is today adjust working hours to the current time
        if date.date() == today.date():
            work_start = datetime.now()
            work_end = work_end.replace(year=today.year, month=today.month, day=today.day)
        
        #adjust start time to the next hour or half hour, if meeting minutes is 30 or the specific booking minutes
        work_start = work_start + timedelta(minutes=(booking_minutes - work_start.minute % booking_minutes) % booking_minutes)
        work_start = work_start.replace(second=0, microsecond=0)

        #create time slots for the day
        day_slots = []

        while work_start < work_end:
            slot_end = work_start + timedelta(minutes=booking_minutes)
            

            #check if the slot collides with any event
            collision = False
            
            for event in events.get(day, []):
                event_start, event_end = event
                if work_start.time() < event_end.time() and slot_end.time() > event_start.time() and event_start != event_end:
                    collision = True
                    break

            if not collision:
                day_slots.append(work_start.time().strftime("%H:%M"))

            work_start = slot_end

        slots.append({"day": day, "slots": day_slots})
    
    return {"error": None, "slots": slots}