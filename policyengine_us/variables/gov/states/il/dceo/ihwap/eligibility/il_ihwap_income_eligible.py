from policyengine_us.model_api import *


class il_ihwap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois IHWAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/6862#7",
        "https://dceo.illinois.gov/communityservices/homeweatherization.html",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.ihwap.eligibility
        p_hhs = parameters(period).gov.hhs
        income = add(spm_unit, period, ["irs_gross_income"])

        # 200% FPL threshold (DOE & HHS funds)
        fpg = spm_unit("spm_unit_fpg", period)
        fpg_limit = fpg * p.fpg_limit

        # 60% SMI threshold (State funds) per HHS LIHEAP-IM-2025-02
        smi = spm_unit("hhs_smi", period)
        smi_limit = smi * p_hhs.liheap.smi_limit

        # Eligible if income is below the higher of the two limits
        # https://www.law.cornell.edu/uscode/text/42/8624#b_2
        income_limit = max_(fpg_limit, smi_limit)
        return income <= income_limit
