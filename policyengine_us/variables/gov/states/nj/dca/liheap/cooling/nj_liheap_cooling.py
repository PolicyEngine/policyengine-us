from policyengine_us.model_api import *


class nj_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP medically necessary cooling benefit"
    unit = USD
    defined_for = "nj_liheap_cooling_eligible"
    reference = (
        # PDF pages 13, 18.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=13",
        # PDF pages 14, 20.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=14",
    )
    documentation = (
        "One-time flat cooling payment made in addition to any heating benefit "
        "(handbook 3.4.A), verified for FY2026 and FY2027."
    )

    def formula(spm_unit, period, parameters):
        return parameters(period).gov.states.nj.dca.liheap.cooling.amount
