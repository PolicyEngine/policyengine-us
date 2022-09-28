from openfisca_us.model_api import *


class or_kicker(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR Kicker"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=19",
        "https://www.oregonlegislature.gov/bills_laws/Pages/OrConst.aspx",  # Article IX Section 14 (4)
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["or"].tax.income.credits.kicker
        return p.percent * tax_unit(
            "or_tax_before_credits_in_prior_year", period
        )
