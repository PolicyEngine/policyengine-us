from policyengine_us.model_api import *


class wv_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "West Virginia LIEAP qualified household size"
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/39948/download?inline=#page=1728,1732",
        "https://bfa.wv.gov/media/40005/download?inline=#page=1729,1734",
    )
    # SPMUnit approximates the co-resident energy-sharing assistance group.
    # Prior-season benefit recipients are excluded by policy, but that receipt
    # history is unavailable. Nonqualified members' income remains countable.
    adds = ["is_citizen_or_legal_immigrant"]
