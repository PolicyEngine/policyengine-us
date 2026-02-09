from policyengine_us.model_api import *


class ia_tanf_net_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF net income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Test 2: Applicants only; recipients skip this test
        is_recipient = spm_unit("is_tanf_enrolled", period)

        p = parameters(period).gov.states.ia.hhs.tanf
        earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])

        # Per IAC 441-41.27(2)"a": 20% earned income deduction (no 58% disregard)
        net_earned = earned * (1 - p.income.earned_income_deduction.rate)
        net_income = net_earned + unearned

        need_standard = spm_unit("ia_tanf_need_standard", period)
        applicant_passes = net_income < need_standard

        return where(is_recipient, True, applicant_passes)
