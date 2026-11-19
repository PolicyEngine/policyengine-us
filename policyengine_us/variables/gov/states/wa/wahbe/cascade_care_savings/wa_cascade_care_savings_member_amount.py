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
        # PDF pages 1, 5 (the PMPM amounts and the three groups).
        "https://www.wahbexchange.org/content/dam/materials/communications/legislative/2025/WAHBE_Final_PY_2026_Cascade_Care_Savings_Maximum_Per_Member_Per_Month_Methodology.pdf#page=1",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/materials/collateral/cc/FinalPY2026CascadeCareSavingsPolicy_Combined.pdf#page=14",
        # PY2027 amounts memo of 2026-10-01: $35 and $20 PMPM with federal
        # subsidies, split at 200% FPL, and $185 PMPM without.
        "https://www.wahbexchange.org/content/dam/materials/communications/legislative/2026/PY-2027-CCS-PMPM-MethodologyMemo.pdf#page=1",
        # Final PY2027 policy, Section 5(1)(b)-(c): two federally subsidized
        # amounts (up to 200% FPL and 201 - 250% FPL), one non-federally
        # subsidized amount, summed per eligible enrollee.
        # PDF pages 6-7
        "https://www.wahbexchange.org/content/dam/materials/communications/policy/2026/Final_PY_2027_Cascade_Care_Savings_Policy.pdf#page=6",
    )
    documentation = (
        "Annual Cascade Care Savings base amount attributable to a single "
        "member, before the household-level statutory cap. The per-member "
        "monthly amount is set by federal-subsidy status (there is NO age "
        "split; the survey figure of $30 per child was incorrect): Group 1 "
        "members eligible for the federal ACA premium tax credit receive the "
        "with-federal-subsidy amount ($55 PMPM for PY2026; for PY2027, $35 "
        "PMPM when the tax unit's income is at or below 200% of the federal "
        "poverty line and $20 PMPM above it, on the exact ratio in "
        "wa_cascade_care_savings_fpl_ratio), and Group 3 "
        "members without a federally recognized immigration status who lack "
        "minimum essential coverage through a state medical assistance program "
        "receive the without-federal-subsidy amount ($250 PMPM for PY2026, "
        "$185 PMPM for PY2027, with no income split), "
        "as do Group 2 members modeled as QHP-eligible enrollees outside the "
        "federal tax family (someone another taxpayer can claim). "
        "Group 3 excludes members eligible for Washington Apple Health "
        "Expansion (undocumented adults) or Apple Health for Kids (children "
        "under 19), per Policy Section 4(1)(f), which also avoids double "
        "counting with the Medicaid-cost proxy in healthcare_benefit_value; it "
        "further requires the member not be premium-tax-credit-eligible, so "
        "Groups 1 and 3 are mutually exclusive. Other Group 2 members "
        "(lawfully present but premium-tax-credit-ineligible for other "
        "reasons) are not separately identifiable in the model and are "
        "documented away. The monthly amount is annualized by "
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
        # structurally mutually exclusive, so the with- and without-subsidy
        # amounts never stack.
        immigration_status = person("immigration_status", period)
        undocumented = (
            immigration_status == immigration_status.possible_values.UNDOCUMENTED
        )
        apple_health_expansion = person("wa_apple_health_expansion_eligible", period)
        apple_health_kids = person("wa_apple_health_kids_eligible", period)
        group_3 = undocumented & ~apple_health_expansion & ~apple_health_kids & ~group_1
        # Group 2: QHP-eligible enrollees outside the federal tax family, who
        # have no federal subsidy (see wa_cascade_care_savings_member_eligible).
        # Count eligible enrollees before the household cap, including a
        # covered child who adds no marginal premium (Policy Section 5(1)(c)).
        group_2 = person("is_aca_marketplace_enrollee", period) & ~person(
            "is_aca_tax_family_member", period
        )
        # Policy Section 5(1)(b): from PY2027 the federally subsidized amount
        # depends on the tax-filing household's income (Section 4(12)) as a
        # share of FPL. The eligibility gate reads the same exact ratio for
        # the 250% limit. right=True keeps a ratio of exactly 2.00 in the
        # band up to 200% FPL.
        fpl_ratio = person.tax_unit("wa_cascade_care_savings_fpl_ratio", period)
        with_subsidy_amount = p.amount.with_federal_subsidy.calc(fpl_ratio, right=True)
        with_subsidy = where(group_1, with_subsidy_amount, 0)
        without_subsidy = where(group_2 | group_3, p.amount.without_federal_subsidy, 0)
        return MONTHS_IN_YEAR * (with_subsidy + without_subsidy)
