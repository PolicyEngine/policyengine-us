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
        "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/07/Income%20Elig%20_Updated%206.29.26.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs.income.fpl_rate
        p_ccdf = parameters(period).gov.hhs.ccdf
        adjusted_income = spm_unit("mo_ccs_adjusted_income", period)
        monthly_fpg = spm_unit("mo_ccs_fpg", period)
        # New applicants use the traditional FPG limit; existing families may
        # qualify up to the higher transitional limit.
        enrolled = spm_unit("mo_ccs_enrolled", period)
        fpg_rate = where(enrolled, p.transitional, p.initial_eligibility)
        # DESE's chart prints each limit to the nearest dollar. Round to cents
        # first so floating-point noise can't move a tie.
        fpg_limit = np.floor(np.round(monthly_fpg * fpg_rate, 2) + 0.5)
        # Adjusted gross income may also not exceed 85% of the state median
        # income (Manual sec. 4.7), and the July 2026 chart applies the lower of
        # its maximum and that amount. On that chart 85% of the median binds for
        # enrolled families from ten people and for new applicants from 17.
        smi_limit = spm_unit("hhs_smi", period) * p_ccdf.income_limit_smi
        return adjusted_income <= min_(fpg_limit, smi_limit)
