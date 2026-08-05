from policyengine_us.model_api import *


class wa_cascade_care_savings_member_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Member eligible for Washington Cascade Care Savings"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-CCS-Policy.pdf#page=8",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-PMPM-Methodology.pdf#page=5",
    )
    documentation = (
        "A person is a Cascade Care Savings enrollee if they fall in Group 1 "
        "or Group 3. Group 1 members are eligible for the federal ACA premium "
        "tax credit (embedding on-Marketplace enrollment, the MFS exclusion, "
        "immigration/TIN status, and the required-contribution income test). "
        "Group 3 members are undocumented residents who are not eligible for "
        "Washington Apple Health Expansion (excluded to avoid double counting "
        "with the Medicaid-cost proxy), leaving the undocumented 138%-250% "
        "FPL residual. Group 2 (lawfully present but premium-tax-credit-"
        "ineligible) is not separately identifiable and is documented away."
    )

    def formula(person, period, parameters):
        group_1 = person("is_aca_ptc_eligible", period)
        immigration_status = person("immigration_status", period)
        undocumented = (
            immigration_status == immigration_status.possible_values.UNDOCUMENTED
        )
        apple_health_expansion = person("wa_apple_health_expansion_eligible", period)
        group_3 = undocumented & ~apple_health_expansion
        return group_1 | group_3
