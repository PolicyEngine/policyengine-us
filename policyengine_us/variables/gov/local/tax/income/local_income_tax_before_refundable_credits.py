from policyengine_us.model_api import *


class local_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax before refundable credits"
    documentation = (
        "Local income, wage, and earnings taxes not already included in the "
        "state-income-tax-before-refunds aggregate."
    )
    unit = USD

    adds = [
        "pa_philadelphia_wage_tax",
        "mo_kansas_city_earnings_tax",
        "mo_st_louis_earnings_tax",
    ]
