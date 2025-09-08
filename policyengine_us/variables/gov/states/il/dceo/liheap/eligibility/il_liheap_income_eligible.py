from policyengine_us.model_api import *


class il_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois LIHEAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    def formula(spm_unit, period, parameters):
        p_hhs = parameters(period).gov.hhs
        p_il = parameters(period).gov.states.il.dceo.liheap

        # Illinois uses 60% of state median income or 200% FPL, whichever is higher
        state_median_income = spm_unit("hhs_smi", period)
        smi_limit = state_median_income * p_hhs.liheap.smi_limit

        # Federal poverty guideline limit
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = fpg * p_il.eligibility.fpg_limit

        # Income concept - using IRS gross income as the base
        income = add(spm_unit, period, ["irs_gross_income"])

        # Eligible if income is below the higher of the two limits
        income_limit = max_(smi_limit, fpg_limit)

        return income <= income_limit
