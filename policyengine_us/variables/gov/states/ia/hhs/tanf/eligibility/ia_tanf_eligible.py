from policyengine_us.model_api import *


class ia_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Iowa TANF"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        gross_income_eligible = spm_unit(
            "ia_tanf_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("ia_tanf_net_income_eligible", period)
        # Test 3: payment standard must exceed countable income
        payment_standard = spm_unit("ia_tanf_payment_standard", period)
        countable_income = spm_unit("ia_tanf_countable_income", period)
        benefit_positive = payment_standard > countable_income

        return (
            demographic_eligible
            & immigration_eligible
            & gross_income_eligible
            & net_income_eligible
            & benefit_positive
        )
