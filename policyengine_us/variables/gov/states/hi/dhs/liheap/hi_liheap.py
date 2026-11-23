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
        # Assume a SOLAR heating type is a net-consuming photovoltaic household,
        # which receives the flat amount.
        heating_type = spm_unit("heating_type", period)
        photovoltaic = heating_type == heating_type.possible_values.SOLAR
        flat = p.subsidized_amount.calc(size)
        # Private dwellings receive points times a statewide value per point.
        # Hawaii sets that value each year from the funds left after the flat
        # payments and the statewide points, and does not publish it. The
        # parameter is the benefit matrix's example value, an estimate, so
        # actual awards differ by year. Callers must send county: regional
        # points read it, and an unsent county falls back to Hawaii County, a
        # neighbor island worth one more point than Oahu.
        points = spm_unit("hi_liheap_points", period)
        return where(subsidized | photovoltaic, flat, points * p.value_per_point)
