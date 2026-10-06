from policyengine_us.model_api import *


class fl_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP household size"
    defined_for = StateCode.FL
    reference = "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=42"

    # Ineligible members are excluded from size, but their otherwise countable
    # income remains included in full. SPM membership approximates the energy
    # economic unit; roomers, separate energy units, special status documents,
    # and tribal-provider assignments are not completely identified by inputs.
    adds = ["is_citizen_or_legal_immigrant"]
