from policyengine_us.model_api import *


class or_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR uncapped non-refundable tax credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        "gov.states.or.tax.income.credits.nonrefundable"
    )
