from policyengine_us.model_api import *


class hi_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF gross income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf",
        "https://humanservices.hawaii.gov/bessd/tanf/",
    )
    defined_for = StateCode.HI
    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
