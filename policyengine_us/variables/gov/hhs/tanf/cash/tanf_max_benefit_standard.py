from policyengine_us.model_api import *

# State-specific max benefit standard variables following CBPP/WRD conventions.
# These return the "headline" tier for cross-state comparison:
# - Shelter-tier states: with-shelter (or highest-shelter) tier
# - Region-tier states: most populous region
# - Work-eligibility states: post-initial-period work-required rate
STATE_TANF_MAX_BENEFIT_STANDARD_VARIABLES = [
    # States with special max benefit standard variables (multi-tier systems)
    "az_tanf_max_benefit_standard",  # With-shelter tier (A1)
    "fl_tca_max_benefit_standard",  # High-shelter tier
    "vt_reach_up_max_benefit_standard",  # Basic needs + max housing
    # For other states, we would add their max benefit standard variables here
    # as they are implemented following CBPP/WRD conventions
]


class tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "TANF maximum benefit standard (CBPP convention)"
    documentation = """
    Maximum TANF benefit amount following CBPP and Welfare Rules Database conventions
    for cross-state comparison. Returns the "headline" tier that researchers expect:

    - Shelter-tier states (AZ, FL): Returns with-shelter or highest-shelter tier
    - Multi-component states (VT): Returns basic needs + maximum housing allowance
    - Region-tier states: Returns most populous region tier (when implemented)
    - Work-eligibility states: Returns post-initial work-required rate (when implemented)

    This is designed for cross-state benefit level comparison and may differ from
    actual benefit calculations, which depend on household-specific characteristics
    (shelter costs, region, work status, etc.). For actual benefit calculation, use
    the state-specific payment standard or maximum benefit variables.

    Reference: CBPP "TANF Benefits Remain Low Despite Recent Increases in Some States"
    and Urban Institute Welfare Rules Database conventions.
    """
    unit = USD
    reference = "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states"

    def formula(spm_unit, period, parameters):
        # Sum all state-specific max benefit standards
        # Only states with multi-tier systems need special variables;
        # states with single payment standards can be added directly here
        return add(spm_unit, period, STATE_TANF_MAX_BENEFIT_STANDARD_VARIABLES)
