from policyengine_us.model_api import *


class ga_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Georgia LIHEAP household size"
    defined_for = StateCode.GA
    # Pages 51-52 exclude nonqualified members from size; page 62 counts income.
    reference = "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=51"

    # The SPM unit approximates the economic unit purchasing energy together.
    # Existing inputs do not identify all roomers, boarders, foster-child
    # elections, or excluded group-quarter arrangements.
    adds = ["is_citizen_or_legal_immigrant"]
