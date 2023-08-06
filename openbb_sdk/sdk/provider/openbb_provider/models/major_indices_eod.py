"""Major indices aggregate end of day price data model."""


from datetime import date, datetime, timedelta
from typing import Optional

from pydantic import Field, PositiveFloat

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class MajorIndicesEODQueryParams(QueryParams, BaseSymbol):
    """Major Indices end of day Query."""

    start_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
        default=date.today() - timedelta(days=30),
    )
    end_date: Optional[date] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=date.today()
    )


class MajorIndicesEODData(Data):
    """Major Indices end of day price data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
    vwap: Optional[float] = Field(description=DATA_DESCRIPTIONS.get("vwap", ""))
