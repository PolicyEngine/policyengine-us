from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class al_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP annualized income limit"
    defined_for = StateCode.AL
    reference = (
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=57",
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.eligibility
        size = spm_unit("al_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        monthly_limit = guideline * p.fpg_rate / MONTHS_IN_YEAR
        # Nearest-dollar, half-up rounding reproduces all 15 printed limits.
        # The FY2026 heating season ends before the May 2026 chart update.
        return np.floor(monthly_limit + 0.5) * MONTHS_IN_YEAR
