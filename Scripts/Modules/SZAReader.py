from os.path import join
from pandas import (
    to_datetime,
    DataFrame,
    read_csv
)


class SZAReader:
    def __init__(
        self,
        params: dict
    ) -> None:
        self.data = None
        self._read(
            params,
        )

    def _read(
        self,
        params: dict
    ) -> DataFrame:
        filename = "sza.csv"
        filename = join(
            params["data_path"],
            filename,
        )
        self.data = read_csv(
            filename,
            parse_dates=True,
            index_col=0
        )

    def get_sza(
        self,
        date: str,
    ) -> float:
        date_ = to_datetime(date)
        daily_data = self.data.loc[date_]
        sza = daily_data["sza"]
        return sza

    def get_dates(
        self,
    ) -> list:
        dates = self.data.index
        dates = list(
            date.strftime("%Y-%m-%d")
            for date in dates
        )
        return dates
