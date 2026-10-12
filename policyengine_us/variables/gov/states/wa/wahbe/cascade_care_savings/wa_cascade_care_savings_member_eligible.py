from policyengine_us.model_api import *


class wa_cascade_care_savings_member_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Member eligible for Washington Cascade Care Savings"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/materials/collateral/cc/FinalPY2026CascadeCareSavingsPolicy_Combined.pdf#page=11",
        "https://www.wahbexchange.org/content/dam/materials/communications/legislative/2025/WAHBE_Final_PY_2026_Cascade_Care_Savings_Maximum_Per_Member_Per_Month_Methodology.pdf#page=5",
    )
    documentation = (
        "A person is a Cascade Care Savings enrollee if they fall in Group 1, "
        "2 or 3. Group 1 members are eligible for the federal ACA premium "
        "tax credit (embedding on-Marketplace enrollment, the MFS exclusion, "
        "immigration/TIN status, and the required-contribution income test). "
        "Group 2 members are QHP-eligible but not eligible for the federal "
        "credit; the model identifies those outside the federal tax family "
        "(someone another taxpayer can claim, or a dependent of a return with "
        "such a filer), since Policy Section 4(2) does not exclude them. "
        "Group 3 members are undocumented residents who lack minimum essential "
        "coverage through a state medical assistance program: they are excluded "
        "if eligible for Washington Apple Health Expansion (undocumented adults) "
        "or Apple Health for Kids (children under 19), per Policy Section "
        "4(1)(f), which also avoids double counting with the Medicaid-cost "
        "proxy in healthcare_benefit_value. Group 3 further requires the member "
        "not be premium-tax-credit-eligible, making Groups 1 and 3 mutually "
        "exclusive. Other Group 2 members (lawfully present but premium-tax-"
        "credit-ineligible for other reasons) are not separately identifiable "
        "and are documented away."
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
        # Group 2: QHP-eligible enrollees outside the federal tax family. The
        # PMPM methodology defines Group 2 as QHP-eligible residents "not
        # eligible for APTC Federal subsidies but eligible for CCS", and
        # Policy Section 4(2) does not list being claimable among its
        # exclusions. pays_aca_premium already excludes undocumented people,
        # so Groups 2 and 3 do not overlap.
        group_2 = person("pays_aca_premium", period) & ~person(
            "is_aca_tax_family_member", period
        )
        return group_1 | group_2 | group_3
