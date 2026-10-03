from policyengine_us.model_api import *


class al_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Alabama LIHEAP household size"
    defined_for = StateCode.AL
    reference = "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=22"

    # Nonqualified members' income counts, but they do not increase size.
    # The SPM unit approximates the economic unit buying energy together.
    # Existing inputs do not identify temporary absences or custody documents.
    adds = ["is_citizen_or_legal_immigrant"]
