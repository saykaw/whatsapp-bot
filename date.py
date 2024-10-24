import datetime
import pytz

def format_ms(ms):
    dt_utc = datetime.datetime.fromtimestamp(1729780010)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    dt_ist = dt_utc.astimezone(ist_timezone)
    formatted_date = dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    time = f'{formatted_date} (IST)'
    return time

def current_time():
    now = datetime.datetime.now()
    ist_timezone = pytz.timezone('Asia/Kolkata')
    dt_ist = now.astimezone(ist_timezone)
    formatted_date = dt_ist.strftime('%d/%m/%Y %H:%M:%S')
    time = f'{formatted_date} (IST)'
    return time