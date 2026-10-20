from policyengine_us.model_api import *


class va_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia rebate"
    documentation = (
        "Virginia one-time rebates are attributed to the return year that determines "
        "eligibility and amount: 2021 for the 2022 payment, 2022 for the 2023 "
        "payment, and 2024 for the 2025 payment. The rebate enters "
        "va_non_refundable_credits in those eligibility years and is limited by "
        "available tax liability. It is zero in other years."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://budget.lis.virginia.gov/item/2023/2/HB6001/Introduced/3/3-5.28/"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.rebate
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
