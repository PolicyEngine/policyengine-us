from policyengine_us.model_api import *


class nj_total_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey total deductions to income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    adds = ["nj_medical_expense_deduction"]
