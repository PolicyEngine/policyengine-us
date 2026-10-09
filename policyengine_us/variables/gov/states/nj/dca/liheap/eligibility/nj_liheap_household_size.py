from policyengine_us.model_api import *


class nj_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP qualified household size"
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 5, 6, 10.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=5",
    )
    documentation = (
        "Qualified SPM members approximate the economic household. The federal "
        "qualified-noncitizen indicator is used without SNAP-specific bars. Foster "
        "residents, tax-dependent students away at school, and separate roomer/boarder "
        "households require correct SPM membership; not all protected immigration "
        "statuses have an enum choice."
    )

    adds = ["is_citizen_or_legal_immigrant"]
