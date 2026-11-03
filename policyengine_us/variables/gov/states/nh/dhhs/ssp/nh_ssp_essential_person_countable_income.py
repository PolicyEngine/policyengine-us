from policyengine_us.model_api import *


class nh_ssp_essential_person_countable_income(Variable):
    value_type = float
    entity = Person
    label = "New Hampshire SSP essential-person countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = "Essential person's net earned income after He-W 654.15 and 654.18 deductions plus gross countable unearned income. Do not subtract the assistance-group standard disregard. Enter once, or the same amount on both applicant spouses."
