import re
from datetime import datetime
from typing import Optional
from persiantools.jdatetime import JalaliDate
import logging

# Configure logging
logger = logging.getLogger(__name__)


def cvt_time(datetime_str: str) -> Optional[str]:
    """
    Converts a Gregorian datetime string to a formatted Jalali datetime string.

    Args:
        datetime_str (str): Input datetime string in the format 'YYYY-MM-DDHH:MM:SS'
                           (e.g., '2025-08-03 11:10:00').

    Returns:
        Optional[str]: Formatted string in the format 'HH:MM:SS YYYY/MM/DD' in Jalali calendar,
                       or None if the input format is invalid.

    Example:
        Input: '2025-08-03 11:10:00'
        Output: '11:10:00 1404/5/12'
    """
    try:
        # Remove any English words and '+' characters
        cleaned_str = remove_english_words(datetime_str).replace('+', '')

        # Parse the datetime string (first 18 characters for 'YYYY-MM-DDHH:MM:SS')
        datetime_obj = datetime.strptime(cleaned_str[:18], "%Y-%m-%d%H:%M:%S")

        # Convert to Jalali date
        jalali_date = JalaliDate.to_jalali(
            datetime_obj.year,
            datetime_obj.month,
            datetime_obj.day
        )

        # Format the output string
        formatted_date = f"{datetime_obj.hour:02d}:{datetime_obj.minute:02d}:{datetime_obj.second:02d} " \
                         f"{jalali_date.year}/{jalali_date.month:02d}/{jalali_date.day:02d}"

        logger.debug("Converted datetime %s to Jalali format: %s", datetime_str, formatted_date)
        return formatted_date

    except ValueError as e:
        logger.error("Failed to convert datetime string %s: %s", datetime_str, str(e))
        return None


def remove_english_words(text: str) -> str:
    """
    Removes English words (sequences of alphabetic characters) from the input string.

    Args:
        text (str): Input string to clean.

    Returns:
        str: String with English words removed.

    Example:
        Input: 'Hello 1403/05/12 World'
        Output: ' 1403/05/12 '
    """
    english_pattern = re.compile(r"[a-zA-Z]+")
    cleaned_text = english_pattern.sub("", text)
    logger.debug("Removed English words from '%s': '%s'", text, cleaned_text)
    return cleaned_text


def jalali_to_gregorian(date_str: str) -> Optional[datetime]:
    """
    Converts a Jalali date string to a Gregorian datetime object.

    Args:
        date_str (str): Jalali date string in the format 'YYYY/MM/DD' (e.g., '1403/2/5').

    Returns:
        Optional[datetime]: Gregorian datetime object, or None if the input format is invalid.

    Example:
        Input: '1403/2/5'
        Output: datetime(2024, 4, 24, 0, 0)
    """
    try:
        # Split the date string and convert to integers
        year, month, day = map(int, date_str.split('/'))

        # Convert Jalali date to Gregorian
        gregorian_date = JalaliDate(year, month, day).to_gregorian()

        # Create and return datetime object
        result = datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        logger.debug("Converted Jalali date %s to Gregorian: %s", date_str, result)
        return result

    except (ValueError, AttributeError) as e:
        logger.error("Failed to convert Jalali date %s: %s", date_str, str(e))
        return None