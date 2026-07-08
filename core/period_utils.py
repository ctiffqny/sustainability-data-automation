import re
from datetime import datetime


# strip data of everything so formatting doesn't affect

def normalize(text):
    if text is None:
        return ""
    text = str(text).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text


# parse and match rows by period (just a safety measure in case the formatting is ever changed)

def parse_period(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    text = str(value).strip().replace("Sept", "Sep")

    for fmt in ("%b-%y", "%b %y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    return None


def normalize_period(value):
    parsed = parse_period(value)
    if parsed:
        return parsed.strftime("%b-%y").lower()
    return str(value).strip().lower()


def periods_match(a, b):
    return normalize_period(a) == normalize_period(b)


def first_day_of_month(date_value):
    return datetime(date_value.year, date_value.month, 1)


def subtract_months(date_value, months):
    year = date_value.year
    month = date_value.month

    for _ in range(months):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1

    return datetime(year, month, 1)