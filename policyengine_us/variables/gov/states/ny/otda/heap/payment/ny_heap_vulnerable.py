from policyengine_us.model_api import *


class ny_heap_vulnerable(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP qualified vulnerable member"
    defined_for = StateCode.NY
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=44,45,49",)
    documentation = "The manual adopts the SNAP benefit-receipt disability criteria. Reuses the existing USDA calculation, including its qualifying veteran and survivor flags. A disability flag alone does not establish receipt or certification. The existing USDA flags approximate detailed VA certification; railroad, FECA and disability-based Medicaid pathways remain incomplete."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.payment
        person = spm_unit.members
        age = person("age", period)
        disabled = person("is_usda_disabled", period)
        vulnerable = (age < p.young_child_age) | (age >= p.elderly_age) | disabled
        return spm_unit.any(
            vulnerable & person("is_citizen_or_legal_immigrant", period)
        )
