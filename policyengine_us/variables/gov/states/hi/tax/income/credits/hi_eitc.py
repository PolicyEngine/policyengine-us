from policyengine_us.model_api import *


class hi_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii earned income tax credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0075.htm"

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.hi.tax.income.credits.eitc.match
        return rate * federal_eitc
