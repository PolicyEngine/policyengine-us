from policyengine_us.model_api import *


class me_relief_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine Relief Rebate"
    defined_for = "me_relief_rebate_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/governor/mills/relief-checks"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.relief_rebate
        head_spouse_count = tax_unit("head_spouse_count", period)
        return head_spouse_count * p.amount
