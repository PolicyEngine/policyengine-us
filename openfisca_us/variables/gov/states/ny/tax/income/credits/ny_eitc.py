from policyengine_us.model_api import *


class ny_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (d)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.ny.tax.income.credits.eitc.match
        tentative_nys_eic = eitc * rate
        household_credit = tax_unit("ny_household_credit", period)
        return max_(0, tentative_nys_eic - household_credit)
