from policyengine_us.model_api import *


class mt_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.income
        countable_income = spm_unit("mt_ccap_countable_income", period)
        # Operational sliding fee scale runs through 200% FPG (graduated tier);
        # the ARM 37.80.202 body text 150% standard / 185% graduated structure is
        # superseded by the published 2025 scale's 185% standard / 200% graduated
        # numbers per the modeling decision (ARM sets the framework; the scale sets
        # the operational numbers).
        #
        # Modeling limitation (graduated 185-200% FPG band is recipient-only): per
        # the Best Beginnings Sliding Fee Scale, graduated eligibility "continues
        # eligibility for Non-TANF families that are deemed over-income," a family
        # "must already be on the Non-TANF program," and at annual redetermination
        # the family would be eligible for Graduated Eligibility. ARM 37.80.202(2)
        # grants graduated eligibility "at annual redetermination." We don't
        # currently track CCAP enrollment status and cannot distinguish new
        # applicants from continuing recipients in a single-period simulation, so
        # the model applies the 200% ceiling to everyone. This over-grants
        # eligibility to new applicants in the 185-200% FPG band.
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_eligible = countable_income <= fpg * p.fpg_limit
        # The 85% SMI hard ineligibility ceiling is operational: it comes from the
        # Sliding Fee Scale and mirrors the federal CCDF maximum at 45 CFR
        # 98.20(a)(2) (no subsidy above 85% of State median income); it is NOT in
        # ARM 37.80.202. For most household sizes the 200% FPG limit binds first, so
        # the SMI cap is operative only for unusually large families (e.g. sizes
        # 11-12 in 2026 once HHS SMI uprating is applied).
        smi = spm_unit("hhs_smi", period)
        smi_eligible = countable_income <= smi * p.income_limit_smi_rate
        income_eligible = fpg_eligible & smi_eligible
        # TANF cash-assistance families are categorically income eligible.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        return income_eligible | tanf_enrolled
