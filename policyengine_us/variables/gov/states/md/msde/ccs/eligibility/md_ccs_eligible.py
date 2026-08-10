from policyengine_us.model_api import *


class md_ccs_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maryland Child Care Scholarship (CCS)"
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.03",
        "https://mgaleg.maryland.gov/2022RS/Chapters_noln/CH_525_hb0995E.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["md_ccs_eligible_child"]) > 0
        income_eligible = spm_unit("md_ccs_income_eligible", period)
        activity_eligible = spm_unit("md_ccs_activity_eligible", period)
        # COMAR 13A.14.06.03F(1) waives the income test for TCA applicants or
        # recipients. We don't track TANF applicants separately from recipients
        # at the moment; the regulation covers both.
        is_tca = spm_unit("is_tanf_enrolled", period)
        receives_ssi = (add(spm_unit, period, ["ssi"]) > 0) | (
            add(spm_unit, period, ["receives_ssi"]) > 0
        )
        return (
            has_eligible_child
            & activity_eligible
            & (income_eligible | is_tca | receives_ssi)
        )
