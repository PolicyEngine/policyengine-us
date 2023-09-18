from policyengine_us.model_api import *


class ky_tuition_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky tuition tax credits (from Form 8863-K)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, parameters):
        #line 12
        tentative_tax_credit = add(tax_unit, period, ["american_opportunity_credit","lifetime_learning_credit"])
        rate = parameters(period).gov.states.ky.tax.income.credits.tuition_tax
        return tentative_tax_credit * rate




