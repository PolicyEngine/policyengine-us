from policyengine_us.model_api import *


class in_tanf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF gross income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/latestArticle/470/10.3",
        "https://www.in.gov/fssa/dfr/files/2800.pdf",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Gross income is the sum of all earned and unearned income
        # before any disregards are applied
        # Per 470 IAC 10.3-4-1 (Gross Income Definition)
        return add(
            spm_unit,
            period,
            [
                "tanf_gross_earned_income",
                "tanf_gross_unearned_income",
            ],
        )
