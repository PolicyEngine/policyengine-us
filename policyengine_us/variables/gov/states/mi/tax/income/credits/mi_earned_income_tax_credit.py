from policyengine_us.model_api import *

# CHANGE THE COPY AND PASTED FROM NY to MI
# policyengine-core test .\policyengine_us\tests\gov\


class mi_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MI EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (d)
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.mi.tax.income.credits.eitc.match
        tentative_nys_eic = eitc * rate
        household_credit = tax_unit("ny_household_credit", period)
        return max_(0, tentative_nys_eic - household_credit)
