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
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-CCS-Policy.pdf#page=11",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-PMPM-Methodology.pdf#page=6",
    )
    documentation = (
        "Washington's state premium assistance program (branded Cascade Care "
        "Savings), administered by the Washington Health Benefit Exchange. The "
        "household base amount sums each eligible member's annual per-member "
        "amount, keyed by federal-subsidy status ($55 PMPM for Group 1 members "
        "with federal subsidies, $250 PMPM for Group 3 members without). The "
        "statutory cap (Policy Section 5(1)(d)-(e)) limits the amount to the "
        "household's net premium after the federal premium tax credit, minus "
        "each eligible member's benchmark premium expectation. "
        "Approximations: SLCSP (the ACA benchmark, second-lowest-cost silver) "
        "proxies both the enrolled plan and the county lowest-cost Cascade Care "
        "Silver plan the Section 5(1)(d) cap actually references, so the two "
        "statutory caps collapse to a single expression (this slightly "
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
        p = parameters(period).gov.states.wa.wahbe.cascade_care_savings
        # Household base amount: sum of each eligible member's annualized
        # per-member PMPM amount (already keyed by federal-subsidy group).
        base_annual = add(tax_unit, period, ["wa_cascade_care_savings_member_amount"])
        # Statutory cap. SLCSP (a MONTH variable summed to the year) proxies
        # both the enrolled plan and the county lowest-cost Cascade Silver plan.
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Benchmark premium expectation is per eligible member, monthly; all
        # members share the household MAGI fraction, so the household annual
        # expectation is the per-member monthly value times the number of
        # eligible members times MONTHS_IN_YEAR.
        magi_fraction = tax_unit("aca_magi_fraction", period)
        expectation_per_member = p.benchmark_expectation.calc(magi_fraction)
        n_members = add(tax_unit, period, ["wa_cascade_care_savings_member_eligible"])
        expectation_annual = MONTHS_IN_YEAR * expectation_per_member * n_members
        cap = max_(0, slcsp_annual - aca_ptc - expectation_annual)
        annual = min_(base_annual, cap)
        eligible = tax_unit("wa_cascade_care_savings_eligible", period)
        return where(eligible, annual, 0)
