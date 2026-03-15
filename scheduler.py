from datetime import datetime
import pytz


def convert_to_utc(user_time_str: str):
    """
    user_time_str example: '2026-03-15 18:15'
    """

    ist = pytz.timezone("Asia/Kolkata")

    local_time = datetime.strptime(user_time_str, "%Y-%m-%d %H:%M")
    local_time = ist.localize(local_time)

    utc_time = local_time.astimezone(pytz.utc)

    return utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")