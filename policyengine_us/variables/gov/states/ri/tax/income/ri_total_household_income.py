from policyengine_us.model_api import *


class ri_total_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island total household income"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
    adds = [
        "ri_household_income",
        "tanf",
        "workers_compensation",
        "child_support_expense",
    ]
    subtracts = ["above_the_line_deductions"]
