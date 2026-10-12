from policyengine_us.model_api import *


class nh_ssp_employment_expenses(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP verified employment expenses"
    definition_period = MONTH
    unit = USD
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = """Monthly verified employment expenses under He-W 654.18, including mandatory payroll deductions and qualifying transportation and dependent-care costs. The formula allows at least the statutory flat amount for aged and disabled workers."""
