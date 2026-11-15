from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class in_ccdf_smi(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Indiana CCDF monthly state median income"
    defined_for = StateCode.IN
    reference = (
        # PDF pages 1-2
        "https://www.in.gov/dA/7fc32972de/CCDFSlidingFeeSchedule_withCopays_2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # Each FSSA schedule pairs the guideline year it adopts with the federal
        # state median income table that starts the October before. The April 5,
        # 2026 schedule caps a family of four at $7,619 a month, 85% of the
        # October 2025 table rounded up, and the March 2023, 2024 and 2025
        # schedules follow the same pattern. The guideline year lag therefore
        # also selects the table.
        p = parameters(period).gov.states["in"].fssa.ccdf.income
        guideline_year = period.start.year - int(p.fpg_year_lag)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, f"{guideline_year - 1}-10-01", parameters)
        return annual_smi / MONTHS_IN_YEAR
