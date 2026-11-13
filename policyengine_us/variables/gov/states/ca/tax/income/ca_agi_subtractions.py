from policyengine_us.model_api import *


class ca_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html",
        # Column A takes the amounts on the filers' own federal return.
        "https://www.ftb.ca.gov/forms/2024/2024-540-ca-instructions.html",
        # PDF pages 4, 13: a dependent's own filing requirement and
        # standard deduction worksheet.
        "https://www.ftb.ca.gov/forms/2024/2024-540-booklet.pdf#page=4",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.agi
        # Each subtraction takes an amount from the filers' federal return.
        # Federal AGI leaves out a tax unit dependent's income, which the
        # dependent reports on their own return, so person-level amounts
        # count only for the head and spouse. Tax-unit-level items, such as
        # us_govt_interest, are added as they are.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
