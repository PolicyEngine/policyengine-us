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
        # CCDF State Plan FFY 2025-2027 Section 3.3.1 waives co-payments for
        # families experiencing homelessness, children with disabilities, and
        # categorically eligible households (foster care and STEP, who pay no
        # co-payment because the state pays 100% of the maximum rate per
        # LAC 28:CLXV.515.B). Section 3.3.1 leaves generic Head Start / Early
        # Head Start enrollment unchecked; only Early Head Start-Child Care
        # Partnership (EHS-CCP) families are waived (Section 3.3.1.vii). We
        # don't track EHS-CCP partnership enrollment at the moment, so that
        # narrow waiver is not modeled.
        eligible_child = person("la_ccap_eligible_child", period)
        special_needs = person("la_ccap_special_needs_child", period)
        waived_child = spm_unit.any(eligible_child & special_needs)
        homeless = spm_unit.household("is_homeless", period.this_year)
        categorical = spm_unit("la_ccap_categorically_eligible", period)
        return waived_child | homeless | categorical
