from policyengine_us.model_api import *


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
    Returns the maximum benefit amount following CBPP and WRD conventions for
    cross-state comparison: basic needs + non-Chittenden housing maximum +
    special housing allowance, multiplied by the ratable reduction.

    Non-Chittenden is used because 13 of Vermont's 14 counties fall in that
    tier, matching WRD's most-counties methodology. The special housing
    allowance is included because CBPP reports it as part of the headline
    standard.

    For actual benefit calculation based on household housing costs, use
    vt_reach_up_payment_standard instead.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance
        basic_needs = spm_unit("vt_reach_up_basic_needs_allowance", period)
        total_needs = basic_needs + p.housing.non_chittenden + p.special_housing
        return total_needs * p.ratable_reduction
