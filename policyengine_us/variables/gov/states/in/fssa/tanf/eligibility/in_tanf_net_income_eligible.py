from policyengine_us.model_api import *


class in_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF net income eligible"
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/latestArticle/470/10.3",
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Net income test - family must have countable income below limit
        # Per 470 IAC 10.3-4-3 (Net Income Test)
        p = parameters(period).gov.states["in"].fssa.tanf.income
        capped_size = min_(spm_unit("spm_unit_size", period), 10)
        countable_income = spm_unit("in_tanf_countable_income", period)
        net_limit = p.net_income_limit[capped_size]
        return countable_income < net_limit
