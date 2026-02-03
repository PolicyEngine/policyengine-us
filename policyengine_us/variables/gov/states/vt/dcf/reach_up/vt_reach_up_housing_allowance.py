from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class vt_reach_up_housing_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up housing allowance"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X"
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Rule 2246: Housing allowance capped by county
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance.housing
        county = spm_unit.household("county", period.this_year)
        in_chittenden = county == County.CHITTENDEN_COUNTY_VT
        # Select maximum based on county
        housing_max = where(in_chittenden, p.chittenden, p.non_chittenden)
        # Cap actual housing costs at maximum
        housing_cost = spm_unit("housing_cost", period)
        return min_(housing_cost, housing_max)
