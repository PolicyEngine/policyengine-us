from policyengine_us.model_api import *


class wv_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "West Virginia LIEAP qualified household size"
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        # PDF pages 1735,1739
        "https://web.archive.org/web/20260302130424/https://bfa.wv.gov/media/39948/download?inline#page=1735",
        # PDF pages 1729,1734
        "https://web.archive.org/web/20261023203756/https://bfa.wv.gov/media/40005/download?inline#page=1729",
    )
    # The manual treats everyone living in the home as one assistance group, whether
    # or not they share heating costs. The SPM unit stands in for that group, so a
    # household with more than one SPM unit is split. Anyone already paid as part of
    # another group leaves the size and income, but that receipt history is
    # unavailable. Nonqualified members' income remains countable.
    adds = ["is_citizen_or_legal_immigrant"]
