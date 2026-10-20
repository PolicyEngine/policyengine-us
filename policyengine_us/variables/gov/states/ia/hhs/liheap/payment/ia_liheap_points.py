from policyengine_us.model_api import *


class ia_liheap_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP total payment matrix points"
    documentation = (
        "Poverty level points plus targeting factor points plus fuel type "
        "points. The total can be zero or negative; the minimum benefit then "
        "applies."
    )
    reference = (
        # Section 11.00, "the amount of payment determined by the total number
        # of matrix points", and Appendix I, Award Calculation.
        # PDF pages 42, 137
        "https://hhs.iowa.gov/media/17262/download?inline#page=42",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IA_BenefitMatrix_Heat-Crisis_2026.pdf#page=1",
    )
    defined_for = StateCode.IA

    adds = [
        "ia_liheap_poverty_points",
        "ia_liheap_targeting_points",
        "ia_liheap_fuel_points",
    ]
