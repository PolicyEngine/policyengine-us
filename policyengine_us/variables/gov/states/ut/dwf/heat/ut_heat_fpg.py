from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ut_heat_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Federal poverty guideline for the Utah HEAT household"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/608_Table_II_Federal_Poverty_Level_(FPL)_Monthly_Income_Limits.htm"

    def formula(spm_unit, period, parameters):
        size = spm_unit("ut_heat_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # Annual 2026 represents the March 2026 snapshot: current-year FPG.
        # Application dates and the March/October transitions are not observed.
        # Parameter backfilling does not verify other historical or future years.
        amount = fpg(max_(size, 1), state_group, period, parameters, year_lag=0)
        return where(size > 0, amount, 0)
