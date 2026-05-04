from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)


class vt_reach_up_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.VT
    documentation = """
    Returns the maximum benefit amount including the full housing allowance,
    following CBPP and WRD conventions for cross-state comparison. This is
    calculated as (basic needs allowance + maximum housing allowance for county)
    × ratable reduction.

    For actual benefit calculation based on household housing costs, use
    vt_reach_up_payment_standard instead.
    """

    def formula(spm_unit, period, parameters):
        # CBPP/WRD convention: report basic needs + maximum housing allowance
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance

        # Get basic needs allowance
        basic_needs = spm_unit("vt_reach_up_basic_needs_allowance", period)

        # Get maximum housing allowance based on county
        county = spm_unit.household("county", period.this_year)
        in_chittenden = county == County.CHITTENDEN_COUNTY_VT
        housing_max = where(in_chittenden, p.housing.chittenden, p.housing.non_chittenden)

        # Apply ratable reduction to total
        total_needs = basic_needs + housing_max
        return total_needs * p.ratable_reduction
