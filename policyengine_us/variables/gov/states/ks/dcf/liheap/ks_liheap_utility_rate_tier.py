from policyengine_us.model_api import *


class KSLIEAPUtilityRateTier(Enum):
    A = "Tier A (lowest rates)"
    B = "Tier B"
    C = "Tier C"
    D = "Tier D"
    E = "Tier E"
    F = "Tier F"
    G = "Tier G"
    H = "Tier H"
    I = "Tier I"
    J = "Tier J (highest rates)"


class ks_liheap_utility_rate_tier(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = KSLIEAPUtilityRateTier
    default_value = KSLIEAPUtilityRateTier.E
    definition_period = YEAR
    label = "Kansas LIEAP utility rate tier"
    documentation = "Utility range tier of the household's primary heating fuel provider in the Kansas LIEAP benefit matrix. Kansas groups fuel providers into tiers A (lowest rates) through J (highest rates) from a periodic rate survey. The tier is a provider attribute the model cannot derive, so it is an input defaulting to the midpoint tier E. The other-fuel matrix has no tier."
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/state-plans/KS_Plan_2026.pdf#page=9",
    )
