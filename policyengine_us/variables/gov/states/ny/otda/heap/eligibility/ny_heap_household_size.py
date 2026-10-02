from policyengine_us.model_api import *


class ny_heap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP qualified household size"
    defined_for = StateCode.NY
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=34,37,44",)
    documentation = "SPM members who are citizens or federally qualified noncitizens. Nonqualified members' income still counts in full. Additional membership exclusions remain unimplemented, including foster members and SSI Code C recipients (existing inputs identify these), and roomers, employees and fleeing felons. The existing immigration enum does not separately identify every additional federally protected status."

    adds = ["is_citizen_or_legal_immigrant"]
