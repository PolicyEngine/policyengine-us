from policyengine_us.model_api import *


class ny_heap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP qualified household size"
    defined_for = StateCode.NY
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=34,37,44",)
    documentation = "SPM members who are citizens or federally qualified noncitizens. Their excluded members' income still counts in full. Foster members, SSI Code C, roomers, employees and fleeing felons cannot be separately identified. The existing immigration enum does not separately identify every additional federally protected status."

    adds = ["is_citizen_or_legal_immigrant"]
