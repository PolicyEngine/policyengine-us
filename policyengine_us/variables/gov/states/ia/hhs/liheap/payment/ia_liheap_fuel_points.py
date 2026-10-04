from policyengine_us.model_api import *


class ia_liheap_fuel_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP fuel type points"
    documentation = (
        "Payment matrix points for the household's primary heating fuel "
        "category: natural gas and electricity 4, liquid propane and fuel oil "
        "5, solid fuel 2, other fuels 0."
    )
    reference = (
        # Appendix I item 3, Fuel/Energy Type (page 137).
        "https://hhs.iowa.gov/media/17262/download?inline#page=137",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.payment
        category = spm_unit("ia_liheap_fuel_category", period)
        return p.fuel_points[category]
