from policyengine_us.model_api import *


class ca_fytc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Foster Youth Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth

        max_amount = add(tax_unit, period, ["ca_fytc_eligible"])

        earned_income = add(tax_unit, period, ["earned_income"])

        reduction_amount = max_(
            0, (earned_income - p.income_threshold) * p.marginal_rate
        )

        return min_(max_amount, earned_income - reduction_amount)
