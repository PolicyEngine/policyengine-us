from policyengine_us.model_api import *


class tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "TANF maximum benefit standard (CBPP convention)"
    documentation = """
    Maximum TANF benefit amount following CBPP and Welfare Rules Database
    conventions for cross-state benefit-level comparison. Returns the
    "headline" tier each state's published research figure is built from:

    - Shelter-tier states (AZ, FL): with-shelter / highest-shelter tier
    - Multi-component states (NY, VT): basic + energy + max shelter, etc.
    - Region-tier states (CA Region 1, CT Region A, KS Group IV): most
      populous region
    - Work-eligibility states (HI): post-initial-period work-required rate

    This differs from actual benefit calculation, which depends on
    household-specific shelter, region, and work status. For real benefit
    calculations use the state-specific payment standard variables.
    """
    unit = USD
    reference = "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states"

    adds = [
        "az_tanf_max_benefit_standard",
        "ca_tanf_max_benefit_standard",
        "ct_tfa_max_benefit_standard",
        "fl_tca_max_benefit_standard",
        "hi_tanf_max_benefit_standard",
        "ks_tanf_max_benefit_standard",
        "ny_tanf_max_benefit_standard",
        "vt_reach_up_max_benefit_standard",
    ]
