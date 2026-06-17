from policyengine_us.model_api import *


class mo_ccs_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Child Care Subsidy based on income"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://web.archive.org/web/20250831220820id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/045/00",
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs.income.fpl_rate
        p_ccdf = parameters(period).gov.hhs.ccdf
        adjusted_income = spm_unit("mo_ccs_adjusted_income", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        # New applicants use the traditional FPG limit; existing families may
        # qualify up to the higher transitional limit.
        enrolled = spm_unit("mo_ccs_enrolled", period)
        fpg_limit = where(
            enrolled,
            monthly_fpg * p.transitional,
            monthly_fpg * p.initial_eligibility,
        )
        # Adjusted gross income may also not exceed 85% of the state median
        # income (CCDF State Plan FFY 2025-2027 secs. 4.7 and 2.3.2). For most
        # household sizes the FPG limit is the lower, binding ceiling; the 85%
        # SMI cap only binds for very large households (roughly 8 or more).
        smi_limit = spm_unit("hhs_smi", period) * p_ccdf.income_limit_smi
        return adjusted_income <= min_(fpg_limit, smi_limit)
