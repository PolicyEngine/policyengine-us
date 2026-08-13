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
        "Group 3 members are undocumented residents who lack minimum essential "
        "coverage through a state medical assistance program: they are excluded "
        "if eligible for Washington Apple Health Expansion (undocumented adults) "
        "or Apple Health for Kids (children under 19), per Policy Section "
        "4(1)(f), which also avoids double counting with the Medicaid-cost "
        "proxy in healthcare_benefit_value. Group 3 further requires the member "
        "not be premium-tax-credit-eligible, making Groups 1 and 3 mutually "
        "exclusive. Group 2 (lawfully present but premium-tax-credit-"
        "ineligible) is not separately identifiable and is documented away."
    )

    def formula(person, period, parameters):
        group_1 = person("is_aca_ptc_eligible", period)
        immigration_status = person("immigration_status", period)
        undocumented = (
            immigration_status == immigration_status.possible_values.UNDOCUMENTED
        )
        # Group 3 excludes members with minimum essential coverage through a
        # state medical assistance program (Policy Section 4(1)(f)): Apple
        # Health Expansion covers undocumented adults and Apple Health for Kids
        # covers children under 19 regardless of immigration status. Excluding
        # both avoids double counting with the Medicaid-cost proxy. Requiring
        # ~group_1 makes Groups 1 and 3 structurally mutually exclusive.
        apple_health_expansion = person("wa_apple_health_expansion_eligible", period)
        apple_health_kids = person("wa_apple_health_kids_eligible", period)
        group_3 = undocumented & ~apple_health_expansion & ~apple_health_kids & ~group_1
        return group_1 | group_3
