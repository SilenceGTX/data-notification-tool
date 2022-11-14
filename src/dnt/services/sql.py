from ast import And
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import create_engine

from dnt.core.messages import Messages
from dnt.core.service import DataServiceBase


def _row2str(row: List[Any]) -> str:
    return ",".join([str(v) for v in row])


class SQLSource(DataServiceBase):
    def __init__(self, name: str, **kwargs: Dict) -> None:
        super().__init__(name)
        self.connection = create_engine(**kwargs)

    def get_messages(self, query: str) -> Messages:
        df: pd.DataFrame = pd.read_sql(query, con=self.connection)
        return Messages(subject=self.name, messages=[_row2str(v) for v in df.values])
