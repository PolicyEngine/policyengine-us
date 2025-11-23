from policyengine_us.model_api import *


class in_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = "in_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("in_tanf_payment_standard", period)
        countable_income = spm_unit("in_tanf_countable_income", period)
        return max_(payment_standard - countable_income, 0)
