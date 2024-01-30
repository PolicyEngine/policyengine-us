from policyengine_us.model_api import *


class spm_unit_paycheck_withholdings(Variable):
    value_type = float
    entity = SPMUnit
    label = "Paycheck withholdings of the SPM unit"
    unit = USD
    definition_period = YEAR

    adds = [
        "employee_payroll_tax",
        "state_income_tax_before_refundable_credits",
        "income_tax_before_credits",
    ]
