from policyengine_us.model_api import *


class in_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Indiana uses both gross and net income tests
        # Per 470 IAC 10.3-4 (Fiscal Eligibility Requirements)

        gross_eligible = spm_unit("in_tanf_gross_income_eligible", period)
        net_eligible = spm_unit("in_tanf_net_income_eligible", period)

        # Must pass both tests
        return gross_eligible & net_eligible
