from policyengine_us.model_api import *


class hi_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP heating or cooling Energy Credit"
    definition_period = YEAR
    unit = USD
    defined_for = "hi_liheap_eligible"
    reference = (
        # PDF pages 10, 13-14
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=10",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=2",
        # Draft FY2026 manual 6.2 and 6.4. PDF pages 69-70
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=69",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        p = parameters(period).gov.states.hi.dhs.liheap.payment
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # The PV flat rate uses the reported billing status independently
        # of the home's space-heating fuel.
        pv_status = spm_unit("hi_liheap_photovoltaic_status", period)
        net_consuming_pv = pv_status == pv_status.possible_values.PV_WITH_NET_USAGE
        flat = p.subsidized_amount.calc(size)
        # Other eligible dwellings receive points times a statewide rate.
        # Hawaii calculates the rate from remaining funds and total points
        # after flat payments. The model uses the matrix's example rate to
        # estimate the award. An omitted county defaults to Hawaii County,
        # which receives one more regional point than Oahu.
        points = spm_unit("hi_liheap_points", period)
        return where(subsidized | net_consuming_pv, flat, points * p.value_per_point)
