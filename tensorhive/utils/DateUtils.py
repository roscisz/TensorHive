from datetime import datetime
from typing import Optional, Union
import logging

log = logging.getLogger(__name__)


class DateUtils:
    input_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    output_date_format = '%Y-%m-%dT%H:%M:%S'
    server_timezone = '+00:00'

    @classmethod
    def parse_string(cls, value: str) -> datetime:
        """
        Parses string representing datetime into datetime. On failure throws ValueError.
        :param value: string representing date
        :return: datetime instance
        """
        try:
            result = datetime.strptime(value, cls.input_date_format)
        except ValueError:
            log.warning('Could not parse string into datetime')
            raise
        else:
            return result

    @classmethod
    def stringify_datetime(cls, value: datetime) -> str:
        """
        Parses datetime object into string.
        :param value: datetime object representing certain date
        :return: string with date that was represented by the datetime object
        """
        return value.strftime(cls.output_date_format) + cls.server_timezone

    @classmethod
    def stringify_datetime_to_api_format(cls, value: datetime) -> str:
        """
        Parses datetime object into string.
        :param value: datetime object representing certain date
        :return: string with date that was represented by the datetime object in the OpenAPI date-time format
        """
        return value.strftime(cls.input_date_format)

    @classmethod
    def try_parse_string(cls, value: Union[str, datetime, None]) -> Optional[datetime]:
        """
        Parses string representing datetime into datetime gracefully.
        :param value: Either str, datetime or None. Parsing will only happen if given str. Otherwise, the original
        value is returned.
        :return: datetime instance or None, if invalid input value was given.
        """
        if isinstance(value, str):
            return cls.parse_string(value)
        if isinstance(value, datetime):
            return value
        return None

    @classmethod
    def try_stringify_datetime(cls, value: Optional[datetime]) -> Optional[str]:
        """
        Parses datetime object into string gracefully.
        :param value: datetime object representing certain date or None.
        :return: string with date that was represented by the datetime object or None if input value was None.
        """
        if value is None:
            return None
        return cls.stringify_datetime(value)
