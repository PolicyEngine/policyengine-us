from policyengine_us.model_api import *


class me_liheap_vulnerable_household(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maine LIHEAP vulnerable household with priority targeting"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = [
        "docs/agents/sources/me-liheap/benefit_calculation.md",
        "docs/agents/sources/me-liheap/federal_regulations.md",
        "42 U.S.C. § 8624(b)(2)(B) - Priority targeting requirements",
    ]

    def formula(spm_unit, period, parameters):
        # Federal LIHEAP targeting requirements per 42 U.S.C. § 8624(b)(2)(B):
        # Priority given to households with high proportion of vulnerable individuals:
        # - Elderly (typically 60+)
        # - Disabled
        # - Young children (typically under 6)

        # Check for elderly household members (age 60+)
        ages = spm_unit("age", period)
        has_elderly = (ages >= 60).any()

        # Check for young children (under 6)
        has_young_children = (ages < 6).any()

        # Check for disabled household members
        is_disabled = spm_unit("is_disabled", period)
        has_disabled = is_disabled.any()

        # Household is vulnerable if it contains any of these priority populations
        return has_elderly | has_young_children | has_disabled
