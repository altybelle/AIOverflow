from datetime import datetime, timedelta

def fullyear(year):
    intervals = []
    
    for month in range(1, 13):
        start_date = datetime(year, month, 1)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = (next_month - timedelta(next_month.day)).replace(hour=23, minute=59, second=59)
    
        intervals.append({ 'start_date': start_date, 'end_date': end_date})

    return intervals
