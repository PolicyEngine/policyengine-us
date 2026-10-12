from policyengine_us.model_api import *


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 3 of 6)"
    documentation = (
        "Schedule D Tax Worksheet line 10: lines 6 and 9, the qualified "
        "dividends and net capital gain left after any Form 4952 line 4g "
        "election. Equals net_capital_gain."
    )
    unit = USD
    reference = dict(
        title="2025 Instructions for Schedule D, Schedule D Tax Worksheet, line 10",
        href="https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=15",
    )
    adds = ["dividend_income_reduced_by_investment_income", "dwks09"]
