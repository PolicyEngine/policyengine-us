from policyengine_us.model_api import *


class wa_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Washington LIHEAP household size"
    documentation = (
        "Citizens and qualified noncitizens in the SPM unit. This approved "
        "mixed-status modeling convention follows existing state implementations; "
        "the Washington plan does not specify its full count/income/share rule. "
        "The SPM unit approximates the household sharing heating responsibility."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=37"
    )
    defined_for = StateCode.WA
    adds = ["is_citizen_or_legal_immigrant"]
