from policyengine_us.model_api import *


class la_ccap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP categorically eligible"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        # LAC 28:CLXV.505: FITAP recipients participating in the STEP program
        # and children in foster care. STEP participation is approximated by
        # TANF enrollment; we don't track STEP work-program status separately
        # at the moment.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return tanf_enrolled | has_foster_child
