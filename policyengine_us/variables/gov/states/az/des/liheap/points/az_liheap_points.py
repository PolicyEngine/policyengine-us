from policyengine_us.model_api import *


class az_liheap_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Arizona LIHEAP total benefit matrix points"
    documentation = "Worksheet total of income points, energy burden points (including portable fuel points) and energy need points; at most 17."
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://des.az.gov/liheap",
    )
    defined_for = StateCode.AZ

    # Worksheet Section 4: "Total All Points: (a+b+c+d+e+f)".
    adds = [
        "az_liheap_income_points",
        "az_liheap_energy_burden_points",
        "az_liheap_energy_need_points",
    ]
