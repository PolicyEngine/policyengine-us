from policyengine_us.model_api import *


class nh_ssp_other_income_deductions(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP other allowable income deductions"
    definition_period = MONTH
    unit = USD
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = """Court-ordered child support and alimony payments deducted under He-W 654.20(a)(1)."""
    # NOTE: Other He-W 654.20-654.21 and 654.15(c) deductions are not derived.
    adds = ["child_support_expense", "alimony_expense"]
