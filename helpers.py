from datetime import datetime
from dateutil.relativedelta import relativedelta

def relative_time(timestamp):
    timestamp = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    diff = relativedelta(now, timestamp)

    if diff.years > 0:
        return f"{diff.years} years ago"
    elif diff.months > 0:
        return f"{diff.months} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.hours > 0:
        return f"{diff.hours} hours ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minutes ago"
    else:
        return "just now"