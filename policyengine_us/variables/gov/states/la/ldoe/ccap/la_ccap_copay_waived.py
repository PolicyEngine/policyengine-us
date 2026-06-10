from policyengine_us.model_api import *


class la_ccap_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP co-payment waived"
    reference = (
        "https://www.louisianabelieves.com/docs/default-source/early-childhood/ccap-sliding-fee-scale.pdf",
        "https://www.doa.la.gov/media/043btqeh/28v165.docx",
    )
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # The sliding fee scale waives co-payments for families experiencing
        # homelessness, children enrolled in Early Head Start-Child Care
        # Partnerships (approximated by Head Start enrollment), children
        # with disabilities, and STEP participants; categorically eligible
        # households (which include STEP participants) also pay no
        # co-payment because the state pays 100% of the maximum rate
        # (LAC 28:CLXV.515.B).
        eligible_child = person("la_ccap_eligible_child", period)
        disabled = person("is_disabled", period.this_year)
        head_start = person("is_enrolled_in_head_start", period.this_year)
        waived_child = spm_unit.any(eligible_child & (disabled | head_start))
        homeless = spm_unit.household("is_homeless", period.this_year)
        categorical = spm_unit("la_ccap_categorically_eligible", period)
        return waived_child | homeless | categorical
