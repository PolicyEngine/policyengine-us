from policyengine_us.model_api import *


class wy_lieap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Wyoming LIEAP household size"
    documentation = (
        "Number of U.S. citizens and qualified noncitizens in the SPM unit. "
        "Excluding other members from household size is a modeling "
        "assumption: Wyoming's FY2026 plan requires immigration-status "
        "verification but does not specify mixed-status household calculations. "
        "The SPM unit approximates the group sharing home heating."
    )
    # FY2026 state plan, section 17.3; the size convention is an assumption.
    reference = "https://dfs.wyo.gov/wp-content/uploads/2025/10/FFY2026-LIEAP-State-Model-Plan.pdf#page=38"
    defined_for = StateCode.WY
    adds = ["is_citizen_or_legal_immigrant"]
