from dnt.core.messages import Message
from dnt.core.base import BaseFormatter
import pandas as pd


class TimeStringFormatter(BaseFormatter):
    @staticmethod
    def format(msg: Message):
        raw_message = msg.message
        for k, v in raw_message.items():
            if isinstance(v, pd.Timestamp):
                raw_message[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        return str(raw_message)

class HumanReadableFormatter(BaseFormatter):
    @staticmethod
    def format(msg: Message):
        raw_message = msg.message
        if isinstance(raw_message["check_time"], pd.Timestamp):
            timestamp = raw_message["check_time"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = str(raw_message["check_time"])
        status = raw_message["check_status"]
        target = raw_message["table_name"] + " (" + raw_message["db"] + ")"
        details = raw_message["details"]

        msg_str = f"""
        {status} on {target}
        Time: {timestamp}
        Details: {details}
        """
        return msg_str
