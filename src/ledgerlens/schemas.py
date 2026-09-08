"""Bounded SEC facts and analysis contracts; money is absolute USD, rates are decimals."""
from datetime import date
from typing import Annotated, Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Finite = Annotated[float, Field(strict=True, allow_inf_nan=False)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


class SecFact(BaseModel):
    start: date | None = None
    end: date
    val: Finite = Field(ge=-1e18, le=1e18)
    accn: str = Field(pattern=r'^\d{10}-\d{2}-\d{6}$')
    filed: date
    form: str = Field(min_length=1, max_length=20)


class Concept(BaseModel):
    units: dict[str, list[SecFact]]


class CompanyFacts(BaseModel):
    cik: int = Field(gt=0, le=9999999999)
    entityName: str = Field(min_length=1, max_length=300)
    facts: dict[str, dict[str, Concept]]

    @model_validator(mode='after')
    def bounded(self) -> 'CompanyFacts':
        count = sum(len(rows) for ns in self.facts.values() for c in ns.values() for rows in c.units.values())
        if count > 200000:
            raise ValueError('Maximum 200000 source observations')
        return self


class Query(StrictModel):
    period_start: date
    period_end: date
    as_of: date
    form: Literal['10-K', '10-Q'] = '10-K'
    tax_rate: Finite = Field(default=0.25, ge=0, le=0.6)

    @model_validator(mode='after')
    def dates(self) -> 'Query':
        if not self.period_start < self.period_end <= self.as_of:
            raise ValueError('Require start < end <= as_of')
        days = (self.period_end - self.period_start).days + 1
        if self.form == '10-K' and not 330 <= days <= 400:
            raise ValueError('Annual analysis requires 330–400 days')
        if self.form == '10-Q' and not 60 <= days <= 110:
            raise ValueError('Quarterly analysis requires 60–110 days, not a YTD interval')
        return self


class AnalysisRequest(StrictModel):
    companyfacts: CompanyFacts
    query: Query
    source_label: Literal['USER PROVIDED DATA', 'DEMO DATA', 'SEC EDGAR'] = 'USER PROVIDED DATA'


class FetchRequest(StrictModel):
    cik: int = Field(gt=0, le=9999999999)
    user_agent: str = Field(min_length=8, max_length=200)


JsonObject = dict[str, Any]
