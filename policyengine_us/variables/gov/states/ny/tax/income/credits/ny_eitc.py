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
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.ny.tax.income.credits
        tentative_nys_eitc = federal_eitc * p.eitc.match
        household_credit = tax_unit("ny_household_credit", period)
        return max_(0, tentative_nys_eitc - household_credit)
