from policyengine_us.model_api import *


class interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest deduction"
    unit = USD
    documentation = "Interest expenses deducted from taxable income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/163"

    formula = sum_of_variables(["interest_expense"])
