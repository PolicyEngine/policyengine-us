from policyengine_us.model_api import *


class me_liheap_crisis_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maine LIHEAP crisis assistance"
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = [
        "https://www.mainehousing.org/programs-services/energy/energydetails/liheap",
        "docs/agents/sources/me-liheap/maine_liheap_overview.md",
        "42 U.S.C. § 8624 - Energy crisis assistance provisions",
    ]

    def formula(spm_unit, period, parameters):
        # Must be LIHEAP eligible first
        liheap_eligible = spm_unit("me_liheap_eligible", period.this_year)

        # Crisis assistance is available November 1 - April 30
        # Based on documentation: "Energy Crisis Intervention Program (ECIP): November 1, 2025 through April 30, 2026"

        current_month = period.start.month

        # Crisis period spans across calendar year: November through April
        # November (11), December (12), January (1), February (2), March (3), April (4)
        in_crisis_period = (current_month >= 11) | (current_month <= 4)

        return liheap_eligible & in_crisis_period
