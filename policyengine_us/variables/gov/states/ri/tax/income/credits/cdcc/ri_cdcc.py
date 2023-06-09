from policyengine_us.model_api import *


class ri_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island child and dependent care credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        fed_cdcc_expenses = tax_unit("cdcc_relevant_expenses", period)
        rate = parameters(period).gov.states.ri.tax.income.credits.cdcc.rate
        return fed_cdcc_expenses * rate
