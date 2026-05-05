from policyengine_us.model_api import *


class hi_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf#page=22",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.HI
    documentation = """
    Returns the steady-state mandatory-work-required Standard of Assistance,
    matching the CBPP and Welfare Rules Database convention for cross-state
    comparison. This is the post-initial-period rate (SOA × 0.80 per HI TANF
    State Plan 11.1 footnote 4) — the same value returned by
    hi_tanf_maximum_benefit, exposed here under the cross-state naming
    convention.
    """

    adds = ["hi_tanf_maximum_benefit"]
