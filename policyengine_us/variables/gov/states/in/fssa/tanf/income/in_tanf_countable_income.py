from policyengine_us.model_api import *


class in_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/files/2800.pdf",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    adds = ["in_tanf_countable_earned_income", "tanf_gross_unearned_income"]
