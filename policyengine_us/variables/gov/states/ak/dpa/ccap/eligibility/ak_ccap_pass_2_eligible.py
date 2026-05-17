from policyengine_us.model_api import *


class ak_ccap_pass_2_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Alaska CCAP PASS II (post-ATAP transitional)"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-41-child-care-assistance-program/section-7-aac-41012-categories-of-assistance",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=144",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.eligibility
        was_recipient = spm_unit("ak_was_atap_recipient", period.this_year)
        months_since_exit = spm_unit("ak_months_since_atap_exit", period)
        within_window = months_since_exit < p.pass_2_transition_months
        base_eligible = spm_unit("ak_ccap_base_eligible", period)
        return was_recipient & within_window & base_eligible
