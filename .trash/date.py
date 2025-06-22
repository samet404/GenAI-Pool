from datetime import datetime

current_date = datetime.now()
day = current_date.day
month = current_date.month
year = current_date.year

# Or as a one-liner:
day, month, year,m = datetime.now().day, datetime.now().month, datetime.now().year, datetime.now().minute
print(day, month, year,m)