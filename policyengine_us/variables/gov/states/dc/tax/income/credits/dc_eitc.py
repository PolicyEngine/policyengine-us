from policyengine_us.model_api import *


class dc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.dc.tax.income.credits.eitc.match
        return eitc * rate
