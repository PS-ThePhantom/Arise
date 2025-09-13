from datetime import date

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