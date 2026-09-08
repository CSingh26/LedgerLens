"""Match facts to a single accession, unit and requested financial duration."""

from datetime import date
from .schemas import CompanyFacts, JsonObject, Query, SecFact

TAGS: dict[str, tuple[str, ...]] = {
    "short_term_borrowings": ("ShortTermBorrowings",),
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ),
    "gross_profit": ("GrossProfit",),
    "ebit": ("OperatingIncomeLoss",),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "cfo": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment",),
    "depreciation": (
        "DepreciationDepletionAndAmortization",
        "DepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
    ),
    "assets": ("Assets",),
    "liabilities": ("Liabilities",),
    "equity": ("StockholdersEquity",),
    "cash": ("CashAndCashEquivalentsAtCarryingValue",),
    "current_assets": ("AssetsCurrent",),
    "current_liabilities": ("LiabilitiesCurrent",),
    "receivables": ("AccountsReceivableNetCurrent",),
    "inventory": ("InventoryNet",),
    "current_debt": ("LongTermDebtCurrent",),
    "long_term_debt": ("LongTermDebtNoncurrent",),
    "interest": ("InterestExpense",),
    "eps": ("EarningsPerShareDiluted",),
    "diluted_shares": ("WeightedAverageNumberOfDilutedSharesOutstanding",),
    "retained_earnings": ("RetainedEarningsAccumulatedDeficit",),
    "cfi": ("NetCashProvidedByUsedInInvestingActivities",),
    "cff": ("NetCashProvidedByUsedInFinancingActivities",),
    "fx_cash": (
        "EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    ),
    "cash_flow_balance": ("CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",),
    "repurchases": ("PaymentsForRepurchaseOfCommonStock",),
}
INSTANT = {
    "short_term_borrowings",
    "assets",
    "liabilities",
    "equity",
    "cash",
    "current_assets",
    "current_liabilities",
    "receivables",
    "inventory",
    "current_debt",
    "long_term_debt",
    "retained_earnings",
    "cash_flow_balance",
}


def rows_for(data: CompanyFacts, name: str, query: Query) -> list[tuple[str, str, SecFact]]:
    unit = "shares" if name == "diluted_shares" else "USD/shares" if name == "eps" else "USD"
    output: list[tuple[str, str, SecFact]] = []
    for tag in TAGS[name]:
        concept = data.facts.get("us-gaap", {}).get(tag)
        if concept:
            output.extend(
                (tag, unit, row)
                for row in concept.units.get(unit, [])
                if row.form in (query.form, query.form + "/A")
                and row.end <= row.filed <= query.as_of
            )
    return output


def evidence(tag: str, unit: str, row: SecFact) -> JsonObject:
    return {
        "value": row.val,
        "tag": tag,
        "unit": unit,
        "start": str(row.start) if row.start else None,
        "end": str(row.end),
        "filed": str(row.filed),
        "accession": row.accn,
        "form": row.form,
        "kind": "structured_fact",
    }


def select_period(
    data: CompanyFacts, query: Query, *, accession: str | None = None, filed: date | None = None
) -> JsonObject:
    revenue = [
        r
        for _, _, r in rows_for(data, "revenue", query)
        if r.start == query.period_start
        and r.end == query.period_end
        and (accession is None or r.accn == accession)
        and (filed is None or r.filed == filed)
    ]
    if not revenue:
        raise ValueError("No eligible revenue for this form, duration and filing cutoff")
    anchor = max(revenue, key=lambda r: (r.filed, r.accn))
    warnings = []
    selected: JsonObject = {}
    for name in TAGS:
        matches = [
            (tag, unit, row)
            for tag, unit, row in rows_for(data, name, query)
            if row.accn == anchor.accn
            and row.filed == anchor.filed
            and row.end == query.period_end
            and (row.start is None if name in INSTANT else row.start == query.period_start)
        ]
        if not matches:
            selected[name] = None
            continue
        # Alias precedence is explicit; conflicting values under that tag remain unavailable.
        preferred = matches[0][0]
        matching = [item for item in matches if item[0] == preferred]
        if len({r.val for _, _, r in matching}) > 1:
            selected[name] = None
            warnings.append(f"Conflicting {name} values within the same filing context")
        else:
            selected[name] = evidence(*matching[0])
    return {
        "facts": selected,
        "accession": anchor.accn,
        "filed": str(anchor.filed),
        "start": str(query.period_start),
        "end": str(query.period_end),
        "form": query.form,
        "days": (query.period_end - query.period_start).days + 1,
        "filing_url": f"https://www.sec.gov/Archives/edgar/data/{data.cik}/{anchor.accn.replace('-', '')}/{anchor.accn}-index.html",
        "warnings": warnings,
    }
