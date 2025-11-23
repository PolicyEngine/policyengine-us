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

    def formula(spm_unit, period, parameters):
        # Sum countable earned and unearned income
        # Per 470 IAC 10.3-4-4 (Countable Income Determination)
        return add(
            spm_unit,
            period,
            [
                "in_tanf_countable_earned_income",
                "in_tanf_countable_unearned_income",
            ],
        )
