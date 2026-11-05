from policyengine_us.model_api import *


class in_ccdf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF income eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=5",
        "https://www.in.gov/dA/3271c7180e/Income-Get-on-CCDF.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.income
        countable_income = spm_unit("in_ccdf_countable_income", period)
        enrolled = spm_unit("is_in_ccdf_enrolled", period)
        # Initial applicants are tested against the get-on share of the
        # federal poverty guideline (127% through Jul 2023, 150% from Aug
        # 2023, 135% from Apr 2026); enrolled recipients are tested at 85%
        # of the state median income. FSSA's charts print each limit to the
        # nearest dollar, with half a dollar going up ($3,073.50 prints as
        # $3,074). Round to cents first so floating-point noise can't move a tie.
        initial_limit = np.floor(
            np.round(spm_unit("in_ccdf_fpg", period) * p.get_on_fpg_rate, 2) + 0.5
        )
        continuing_limit = spm_unit("hhs_smi", period) * p.stay_on_smi_rate
        income_limit = where(enrolled, continuing_limit, initial_limit)
        return countable_income <= income_limit
