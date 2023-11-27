"""FMP Insider Trading Model."""

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_fmp.utils.definitions import TRANSACTION_TYPES
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, model_validator


class FMPInsiderTradingQueryParams(InsiderTradingQueryParams):
    """FMP Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """

    transaction_type: Optional[Union[List[TRANSACTION_TYPES], str]] = Field(
        default=["P-Purchase"],
        description="Type of the transaction.",
        alias="transactionType",
    )

    @model_validator(mode="after")
    @classmethod
    def validate_transaction_type(cls, values: "InsiderTradingQueryParams"):
        """Validate the transaction type."""
        if isinstance(values.transaction_type, list):
            values.transaction_type = ",".join(values.transaction_type)
        return values


class FMPInsiderTradingData(InsiderTradingData):
    """FMP Insider Trading Data."""

    __alias_dict__ = {
        "owner_cik": "reportingCik",
        "owner_name": "reportingName",
        "owner_title": "typeOfOwner",
        "security_type": "securityName",
        "transaction_price": "price",
        "acquisition_or_disposition": "acquistionOrDisposition",
        "filing_url": "link",
    }

    form_type: str = Field(description="Form type of the insider trading.")


class FMPInsiderTradingFetcher(
    Fetcher[
        FMPInsiderTradingQueryParams,
        List[FMPInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPInsiderTradingQueryParams:
        """Transform the query params."""
        return FMPInsiderTradingQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: FMPInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v4/insider-trading"
        query_str = get_querystring(query.model_dump(by_alias=True), ["page"])

        data: List[Dict] = []

        limit_reached = 0
        page = 0

        while limit_reached <= query.limit:
            url = f"{base_url}?{query_str}&page={page}&apikey={api_key}"
            data.extend(await get_data_many(url, **kwargs))
            limit_reached += len(data)
            page += 1

        return data[: query.limit]

    @staticmethod
    def transform_data(
        query: FMPInsiderTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPInsiderTradingData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["filingDate"], reverse=True)
        return [FMPInsiderTradingData.model_validate(d) for d in data]
