from policyengine_us.model_api import *


class local_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax"
    documentation = "Local income, wage, and earnings taxes."
    unit = USD

    adds = [
        "nyc_income_tax",
        "pa_philadelphia_wage_tax",
        "mo_kansas_city_earnings_tax",
        "mo_st_louis_earnings_tax",
    ]
