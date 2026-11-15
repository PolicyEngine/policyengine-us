from policyengine_us.model_api import *


class mo_ccs_funding_rate(Variable):
    value_type = float
    entity = SPMUnit
    unit = "/1"
    label = "Missouri Child Care Subsidy share of the remaining base rate funded"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://web.archive.org/web/20250831220820id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/045/00",
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060",
        "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/07/Income%20Elig%20_Updated%206.29.26.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # Manual 2010.045.00 funds traditional families at the full base rate and
        # each Transitional Child Care level at a reduced share. DESE's chart prints
        # each level's top as the nearest dollar of a multiple of the guideline, and
        # income above a top falls in the next level. Round to cents first so
        # floating-point noise can't move a tie.
        scale = parameters(period).gov.states.mo.dese.ccs.transitional.funding_rate
        adjusted_income = spm_unit("mo_ccs_adjusted_income", period)
        monthly_fpg = spm_unit("mo_ccs_fpg", period)
        funding_rate = np.full_like(adjusted_income, scale.amounts[0])
        for threshold, amount in zip(scale.thresholds[1:], scale.amounts[1:]):
            level_top = np.floor(np.round(monthly_fpg * threshold, 2) + 0.5)
            funding_rate = where(adjusted_income > level_top, amount, funding_rate)
        return funding_rate
