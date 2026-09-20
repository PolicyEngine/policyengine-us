from policyengine_us.model_api import *


class requires_childcare_under_court_order(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Requires child care under a court order"
    documentation = (
        "Whether a court order, or a case plan implementing court-ordered "
        "supervision, specifically requires supervised child care for this "
        "person. General court supervision alone does not establish this "
        "requirement."
    )
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=29",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2025/CCAP%20ML%203909%20Effective%20May.1.2025.pdf#page=3",
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",
    )
