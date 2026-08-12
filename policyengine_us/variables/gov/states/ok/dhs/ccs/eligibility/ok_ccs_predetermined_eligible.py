from policyengine_us.model_api import *


class ok_ccs_predetermined_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oklahoma Child Care Subsidy predetermined eligible"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = "https://okrules.elaws.us/oac/340:40-7-1"

    def formula(spm_unit, period, parameters):
        # Households receiving public assistance (TANF, including Supported
        # Permanency, State Supplemental Payments, or Refugee Resettlement
        # Program cash assistance) or Supplemental Security Income are
        # predetermined eligible with no family share copayment
        # (OAC 340:40-7-1(b)(1)). We model the TANF and SSI pathways; we don't
        # track Oklahoma State Supplemental Payments or Refugee Resettlement
        # cash assistance at the moment. is_tanf_enrolled is used instead of a
        # computed TANF variable to avoid the circular dependency through the
        # TANF dependent care deduction.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        receives_ssi = add(spm_unit, period, ["ssi"]) > 0
        return is_tanf_enrolled | receives_ssi
