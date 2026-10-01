from policyengine_us.model_api import *


class ny_heap_vulnerable(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP qualified vulnerable member"
    defined_for = StateCode.NY
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=44,45,49",)
    documentation = "Permanent-disability input and SSI/SSDI receipt approximate HEAP disability certification. Detailed VA, railroad, FECA and disability-based Medicaid certification pathways are not separately identified."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.payment
        person = spm_unit.members
        age = person("age", period)
        disabled = (
            person("is_permanently_and_totally_disabled", period)
            | (person("ssi", period) > 0)
            | (person("social_security_disability", period) > 0)
        )
        vulnerable = (age < p.young_child_age) | (age >= p.elderly_age) | disabled
        return spm_unit.any(
            vulnerable & person("is_citizen_or_legal_immigrant", period)
        )
