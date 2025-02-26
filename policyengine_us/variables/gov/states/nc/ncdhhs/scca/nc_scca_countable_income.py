from policyengine_us.model_api import *


class nc_scca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "North Carolina Subsidized Child Care Assistance program countable income"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=11"

    adds = ["snap_earned_income", "snap_unearned_income"]
