from policyengine_us.model_api import *


class wa_cascade_care_savings(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington Cascade Care Savings"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        # Final PY2026 policy: Section 5(1)(c) (per-member build-up) and 5(1)(d)
        # (the household cap), p.14; Attachment 1, p.3, lists the benchmark
        # premium expectation among the concepts "not included in the final
        # policy".
        "https://www.wahbexchange.org/content/dam/wahbe-assets/materials/collateral/cc/FinalPY2026CascadeCareSavingsPolicy_Combined.pdf#page=14",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/materials/collateral/cc/FinalPY2026CascadeCareSavingsPolicy_Combined.pdf#page=3",
        # Final PY2026 PMPM methodology (memo of 2025-09-30): the $55 and $250
        # amounts on p.1, Wakely's 2025-vs-2026 exhibit on p.7.
        "https://www.wahbexchange.org/content/dam/materials/communications/legislative/2025/WAHBE_Final_PY_2026_Cascade_Care_Savings_Maximum_Per_Member_Per_Month_Methodology.pdf#page=1",
    )
    documentation = (
        "Washington's state premium assistance program (branded Cascade Care "
        "Savings), administered by the Washington Health Benefit Exchange. The "
        "household base amount sums each eligible member's annual per-member "
        "amount, keyed by federal-subsidy status ($55 PMPM for Group 1 members "
        "with federal subsidies, $250 PMPM for Group 3 members without). The "
        "cap (Policy Section 5(1)(d)) limits the amount to the lesser of the "
        "household's net premium after the federal premium tax credit and "
        "the net premium its eligible members would pay in the county's "
        "lowest-cost Cascade Care Silver plan. There is NO benchmark premium "
        "expectation: the final PY2026 policy's Attachment 1 lists it among "
        "the concepts 'included in the final draft ... but not included in "
        "the final policy', and Section 5 as adopted subtracts nothing from "
        "the residual. "
        "Approximations: SLCSP (the ACA benchmark, second-lowest-cost silver) "
        "proxies both the enrolled plan and the county lowest-cost Cascade Care "
        "Silver plan the Section 5(1)(d) cap actually references, so the two "
        "caps collapse to a single expression (this slightly "
        "overstates the cap since SLCSP exceeds the lowest-cost silver); the "
        "Cascade "
        "standard-plan enrollment requirement is treated as met by any "
        "otherwise-eligible Marketplace enrollee (a takeup-style "
        "approximation); and full-year enrollment is assumed via the "
        "MONTHS_IN_YEAR annualization. Cascade Care Savings is excluded from "
        "federal gross income under the general welfare exception, so it is "
        "not routed through taxable income, and it is paid monthly to issuers "
        "rather than as a tax credit, so no reconciliation or tax-return "
        "interaction is modeled."
    )

    def formula(tax_unit, period, parameters):
        # Household base amount: sum of each eligible member's annualized
        # per-member PMPM amount (already keyed by federal-subsidy group).
        base_annual = add(tax_unit, period, ["wa_cascade_care_savings_member_amount"])
        # Cap (Policy Section 5(1)(d)): the premium left after the federal
        # credit. SLCSP (a MONTH variable summed to the year) proxies both the
        # enrolled plan and the county lowest-cost Cascade Silver plan, so the
        # lesser-of collapses to one expression.
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        cap = max_(0, slcsp_annual - aca_ptc)
        annual = min_(base_annual, cap)
        eligible = tax_unit("wa_cascade_care_savings_eligible", period)
        return where(eligible, annual, 0)
