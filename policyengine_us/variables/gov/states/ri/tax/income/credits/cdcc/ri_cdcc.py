from policyengine_us.model_api import *


class ri_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island child and dependent care credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        ri_income_tax = tax_unit("ri_income_tax", period)
        fed_cdcc = tax_unit("cdcc", period)
        rate = parameters(period).gov.states.ri.tax.income.credits.cdcc.rate
        return min_(fed_cdcc * rate, ri_income_tax)
