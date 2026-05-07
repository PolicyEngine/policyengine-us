from policyengine_us.model_api import *


class ks_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.KS
    documentation = """
    Returns the Group IV non-shared-living payment standard (basic + $135
    shelter), matching the CBPP and Welfare Rules Database convention for
    cross-state comparison. Group IV covers Johnson County (the most populous
    in Kansas). This is the same value returned by ks_tanf_maximum_benefit,
    exposed here under the cross-state naming convention.
    """

    adds = ["ks_tanf_maximum_benefit"]
