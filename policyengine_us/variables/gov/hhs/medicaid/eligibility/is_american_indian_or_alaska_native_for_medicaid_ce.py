from policyengine_us.model_api import *


class is_american_indian_or_alaska_native_for_medicaid_ce(Variable):
    value_type = bool
    entity = Person
    label = "American Indian or Alaska Native for Medicaid community engagement"
    documentation = (
        "Whether this person qualifies for the Medicaid community engagement "
        "American Indian or Alaska Native exclusion, including Indian, Urban "
        "Indian, California Indian, or other Indian Health Service eligibility "
        "status."
    )
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=5",
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
    )
