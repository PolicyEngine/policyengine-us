from policyengine_us.model_api import *


class il_liheap_regular_heating(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP regular heating payment"
    unit = USD
    definition_period = YEAR
    defined_for = "il_liheap_eligible"
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/IL_BenefitMatrix_Heat-Cool_2026.pdf#page=2"

    adds = ["il_liheap_base_payment"]
