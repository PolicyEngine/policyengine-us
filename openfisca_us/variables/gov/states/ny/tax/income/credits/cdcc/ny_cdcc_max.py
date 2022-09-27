from openfisca_us.model_api import *


class ny_cdcc_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum NY CDCC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c)

    def formula(tax_unit, period, parameters):
        ny_cdcc = parameters(period).gov.states.ny.tax.income.credits.cdcc
        count_eligible = tax_unit("count_cdcc_eligible", period)
        cdcc_expenses = tax_unit("cdcc_relevant_expenses", period)
        lower_earnings = tax_unit("min_head_spouse_earned", period)
        ny_cap = ny_cdcc.max.calc(count_eligible)
        return min_(cdcc_expenses, min_(ny_cap, lower_earnings))
