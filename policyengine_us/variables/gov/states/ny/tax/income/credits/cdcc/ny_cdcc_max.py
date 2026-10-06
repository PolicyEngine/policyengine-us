from policyengine_us.model_api import *


class ny_cdcc_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum NY CDCC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (c)
        "https://www.tax.ny.gov/pdf/2022/inc/it216i_2022.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        ny_cdcc = parameters(period).gov.states.ny.tax.income.credits.cdcc
        count_eligible = tax_unit("count_cdcc_eligible", period)
        # Form IT-216 line 5 caps the total qualified expenses (line 3a) at the
        # New York amount for the number of qualifying persons, not at the
        # federal Form 2441 limit.
        cdcc_expenses = tax_unit("tax_unit_childcare_expenses", period) + add(
            tax_unit, period, ["care_expenses"]
        )
        ny_cap = ny_cdcc.max.calc(count_eligible)
        # Line 5 also takes line 3b (Worksheet 1, line 16): the smaller of the
        # New York cap and the expenses, each less the excluded employer
        # dependent care benefits (line 13). If zero or less, no credit.
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        line_5 = max_(min_(cdcc_expenses, ny_cap) - exclusion, 0)
        lower_earnings = tax_unit("min_head_spouse_earned", period)
        return min_(line_5, lower_earnings)
