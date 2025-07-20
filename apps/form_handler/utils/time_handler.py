import datetime
import re
from persiantools.jdatetime import JalaliDate
from datetime import datetime


def cvt_time(datetime_str):
    datetime_str = remove_english_words(datetime_str).replace('+', '')
    datetime_obj = datetime.strptime(datetime_str[:18], "%Y-%m-%d%H:%M:%S")

    year = datetime_obj.year
    month = datetime_obj.month
    day = datetime_obj.day
    hour = datetime_obj.hour
    minute = datetime_obj.minute
    second = datetime_obj.second
    date2 = JalaliDate.to_jalali(year, month, day)
    date2 = f'{date2.year}/{date2.month}/{date2.day}'

    return f'{hour}:{minute}:{second} {date2} '


def remove_english_words(text):
    english_pattern = re.compile("[a-zA-Z]+")
    return english_pattern.sub("", text)


def jalali_to_gregorian(date_str):
    # تاریخ شمسی ورودی به فرمت 'YYYY/MM/DD' مثل '1403/2/5'
    year, month, day = map(int, date_str.split('/'))  # تقسیم رشته تاریخ و تبدیل به اعداد
    jalali_date = JalaliDate(year, month, day)  # ساخت شیء تاریخ جلالی
    gregorian_date = jalali_date.to_gregorian()  # تبدیل به تاریخ میلادی
    return datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)  # بازگشت شیء datetime میلادی
