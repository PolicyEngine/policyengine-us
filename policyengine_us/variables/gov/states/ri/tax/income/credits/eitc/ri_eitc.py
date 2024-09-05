from policyengine_us.model_api import *


class ri_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island earned income tax credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        rate = parameters(period).gov.states.ri.tax.income.credits.eitc.match
        return federal_eitc * rate
