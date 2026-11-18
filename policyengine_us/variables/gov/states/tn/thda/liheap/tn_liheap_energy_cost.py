from policyengine_us.model_api import *


class tn_liheap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Tennessee LIHEAP annual energy cost"
    documentation = (
        "Annual household energy bills of every fuel, used for the active "
        "energy account test and as the numerator of the energy burden."
    )
    defined_for = StateCode.TN
    reference = (
        # PDF pages 8, 32-33
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/TN_Plan_2026.pdf#page=9",
    )

    adds = "gov.states.tn.thda.liheap.payment.energy_cost_sources"
