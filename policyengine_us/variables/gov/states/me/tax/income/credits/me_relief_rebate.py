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
        # P.L. 2021, c. 635, Part L-3 pays each eligible resident who "may not
        # be claimed as a dependent on another taxpayer's return".
        recipients = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        return recipients * p.amount
