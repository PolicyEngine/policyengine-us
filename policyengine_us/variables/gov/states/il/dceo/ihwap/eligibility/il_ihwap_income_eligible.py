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

        # IL IHWAP Program Year N uses FPL/SMI from year N-1
        # e.g., PY2026 uses FPL 2025-01-01 + SMI 2024-10-01
        prior_year = str(period.start.year - 1)

        # 200% FPL threshold (all funding sources)
        fpg = spm_unit("spm_unit_fpg", prior_year)
        fpg_limit = fpg * p.fpg_limit

        # 60% SMI threshold (State funds only) per HHS LIHEAP-IM-2025-02
        # Only applies to households larger than smi_threshold_size
        smi = spm_unit("hhs_smi", prior_year)
        smi_limit = smi * p_hhs.liheap.smi_limit

        # Sizes 1-7: 200% FPL only
        # Sizes 8+: max(200% FPL, 60% SMI)
        size = spm_unit("spm_unit_size", period)
        large_household_limit = max_(fpg_limit, smi_limit)
        income_limit = where(
            size > p.smi_threshold_size,
            large_household_limit,
            fpg_limit,
        )
        return income <= income_limit
