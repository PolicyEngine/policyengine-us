from policyengine_us.model_api import *


class id_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Idaho LIHEAP eligible household size"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=9"
    # The SPM unit approximates the economic unit sharing heating costs.
    adds = ["is_citizen_or_legal_immigrant"]
