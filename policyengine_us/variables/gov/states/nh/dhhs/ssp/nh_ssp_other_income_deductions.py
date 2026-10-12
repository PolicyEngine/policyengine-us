from policyengine_us.model_api import *


class nh_ssp_other_income_deductions(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP other allowable income deductions"
    definition_period = MONTH
    unit = USD
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = """Verified court-ordered payments, garnishments, qualifying training expenses and dependent allocations under He-W 654.20 and 654.21. Include any approved additional ANB employment-plan disregard under He-W 654.15(c)."""
