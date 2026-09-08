"""Fictional, deterministic teaching statements; never used after an input failure."""

from datetime import date
from .schemas import AnalysisRequest, CompanyFacts, Query

VALUES = {
    "ShortTermBorrowings": (0, 0, 0),
    "RevenueFromContractWithCustomerExcludingAssessedTax": (1000, 800, 600),
    "GrossProfit": (400, 300, 200),
    "OperatingIncomeLoss": (200, 140, 100),
    "NetIncomeLoss": (120, 80, 60),
    "NetCashProvidedByUsedInOperatingActivities": (180, 120, 90),
    "PaymentsToAcquirePropertyPlantAndEquipment": (50, 40, 30),
    "DepreciationDepletionAndAmortization": (30, 20, 15),
    "Assets": (1200, 1000, 800),
    "Liabilities": (700, 600, 500),
    "StockholdersEquity": (500, 400, 300),
    "CashAndCashEquivalentsAtCarryingValue": (100, 80, 60),
    "AssetsCurrent": (400, 320, 240),
    "LiabilitiesCurrent": (200, 160, 120),
    "AccountsReceivableNetCurrent": (100, 90, 80),
    "InventoryNet": (90, 80, 70),
    "LongTermDebtCurrent": (20, 20, 20),
    "LongTermDebtNoncurrent": (280, 280, 260),
    "InterestExpense": (20, 18, 16),
    "EarningsPerShareDiluted": (1.5, 1, 0.75),
    "WeightedAverageNumberOfDilutedSharesOutstanding": (80, 80, 80),
    "RetainedEarningsAccumulatedDeficit": (300, 210, 150),
    "NetCashProvidedByUsedInInvestingActivities": (-70, -50, -40),
    "NetCashProvidedByUsedInFinancingActivities": (-90, -50, -30),
    "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": (
        0,
        0,
        0,
    ),
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": (100, 80, 60),
    "PaymentsForRepurchaseOfCommonStock": (25, 20, 15),
}
INSTANT = {
    "ShortTermBorrowings",
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue",
    "AssetsCurrent",
    "LiabilitiesCurrent",
    "AccountsReceivableNetCurrent",
    "InventoryNet",
    "LongTermDebtCurrent",
    "LongTermDebtNoncurrent",
    "RetainedEarningsAccumulatedDeficit",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
}


def demo_request() -> AnalysisRequest:
    concepts = {}
    for tag, values in VALUES.items():
        unit = (
            "shares"
            if tag.startswith("WeightedAverage")
            else "USD/shares"
            if tag.startswith("EarningsPerShare")
            else "USD"
        )
        observations = []
        for year, value in zip([2025, 2024, 2023], values):
            row = dict(
                end=f"{year}-12-31",
                val=value * (1 if unit == "USD/shares" else 1000000),
                accn="0000000001-26-000001",
                filed="2026-02-01",
                form="10-K",
            )
            if tag not in INSTANT:
                row["start"] = f"{year}-01-01"
            observations.append(row)
        concepts[tag] = {"units": {unit: observations}}
    return AnalysisRequest(
        companyfacts=CompanyFacts.model_validate(
            {"cik": 1, "entityName": "DEMO DATA — Meridian Tools", "facts": {"us-gaap": concepts}}
        ),
        query=Query(
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            as_of=date(2026, 3, 1),
            form="10-K",
        ),
        source_label="DEMO DATA",
    )
