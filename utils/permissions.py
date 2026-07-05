from datetime import date

def validate_log_date(log_date, role):
    if role != "admin" and log_date > date.today():
        return False, "Readers can only log today or past dates."
    return True, ""
