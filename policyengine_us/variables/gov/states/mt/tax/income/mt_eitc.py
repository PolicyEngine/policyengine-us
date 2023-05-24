from policyengine_us.model_api import *


class mt_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.earned_income

        eligible = tax_unit("mt_eitc_eligible", period)

        #How to take output of mt_child_count into rate file?

        child_count = tax_unit("mt_child_count", period)

        max_credits = tax_unit("rate", period)

        return eligible * max_credits
