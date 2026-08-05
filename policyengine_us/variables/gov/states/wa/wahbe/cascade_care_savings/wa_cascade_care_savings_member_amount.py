from policyengine_us.model_api import *


class wa_cascade_care_savings_member_amount(Variable):
    value_type = float
    entity = Person
    label = "Washington Cascade Care Savings annual amount per member"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-PMPM-Methodology.pdf#page=1",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-CCS-Policy.pdf#page=11",
    )
    documentation = (
        "Annual Cascade Care Savings base amount attributable to a single "
        "member, before the household-level statutory cap. The per-member "
        "monthly amount is set by federal-subsidy status (there is NO age "
        "split; the survey figure of $30 per child was incorrect): Group 1 "
        "members eligible for the federal ACA premium tax credit receive the "
        "with-federal-subsidy amount ($55 PMPM for PY2026), and Group 3 "
        "members without a federally recognized immigration status who lack "
        "minimum essential coverage through a state medical assistance program "
        "receive the without-federal-subsidy amount ($250 PMPM for PY2026). "
        "Group 3 excludes members eligible for Washington Apple Health "
        "Expansion (undocumented adults) or Apple Health for Kids (children "
        "under 19), per Policy Section 4(1)(f), which also avoids double "
        "counting with the Medicaid-cost proxy in healthcare_benefit_value; it "
        "further requires the member not be premium-tax-credit-eligible, so "
        "Groups 1 and 3 are mutually exclusive. Group 2 (lawfully present but "
        "premium-tax-credit-ineligible) is not separately identifiable in the "
        "model and is documented away. The monthly amount is annualized by "
        "MONTHS_IN_YEAR, assuming full-year enrollment."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.wahbe.cascade_care_savings
        # Group 1: eligible for the federal ACA premium tax credit. This gate
        # embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, immigration/TIN status, and the required-contribution
        # income test.
        group_1 = person("is_aca_ptc_eligible", period)
        # Group 3: undocumented residents who lack minimum essential coverage
        # through a state medical assistance program (Policy Section 4(1)(f)).
        # Exclude Apple Health Expansion (undocumented adults) and Apple Health
        # for Kids (children under 19) enrollees to avoid double counting with
        # the Medicaid-cost proxy. Requiring ~group_1 makes Groups 1 and 3
        # structurally mutually exclusive, preventing $55 + $250 stacking.
        immigration_status = person("immigration_status", period)
        undocumented = (
            immigration_status == immigration_status.possible_values.UNDOCUMENTED
        )
        apple_health_expansion = person("wa_apple_health_expansion_eligible", period)
        apple_health_kids = person("wa_apple_health_kids_eligible", period)
        group_3 = undocumented & ~apple_health_expansion & ~apple_health_kids & ~group_1
        with_subsidy = where(group_1, p.amount.with_federal_subsidy, 0)
        without_subsidy = where(group_3, p.amount.without_federal_subsidy, 0)
        return MONTHS_IN_YEAR * (with_subsidy + without_subsidy)
