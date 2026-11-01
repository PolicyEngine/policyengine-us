from policyengine_us.model_api import *


class ut_heat_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah HEAT annual income limit"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/608_Table_II_Federal_Poverty_Level_(FPL)_Monthly_Income_Limits.htm"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.eligibility
        # The published 150% column uses unrounded annual FPG, rather than
        # multiplying the upward-rounded monthly 100% benefit denominator.
        return spm_unit("ut_heat_fpg", period) * p.income_limit
