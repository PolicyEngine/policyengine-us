from policyengine_us.model_api import *


class amt_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    adds = [
        "taxable_income",
        "amt_excluded_deductions",
        "amt_separate_addition",
    ]
