from policyengine_us.model_api import *


class ri_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island earned income tax credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        fed_eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.ri.tax.income.credits.eitc.match
        return fed_eitc * rate
