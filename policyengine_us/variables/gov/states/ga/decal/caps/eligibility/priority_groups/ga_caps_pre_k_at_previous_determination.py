from policyengine_us.model_api import *


class ga_caps_pre_k_at_previous_determination(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Child attended Georgia's Pre-K Program at the family's initial Georgia CAPS application or previous eligibility determination"
    defined_for = StateCode.GA
    reference = "https://caps.decal.ga.gov/Assets/downloads/CAPS_Letter_from_Elisabetta_Kasfir_Families_07.01.2024.pdf#page=1"
