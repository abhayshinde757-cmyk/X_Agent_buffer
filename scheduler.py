from datetime import datetime, timedelta
import pytz


def get_current_utc():
    """
    Returns current time + 2 minutes in UTC format required by Buffer API.
    A small buffer is added because Buffer requires dueAt to be in the future.
    """
    ist = pytz.timezone("Asia/Kolkata")
    
    current_time = datetime.now(ist) + timedelta(minutes=2)
    utc_time = current_time.astimezone(pytz.utc)

    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")