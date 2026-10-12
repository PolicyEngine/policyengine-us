from policyengine_us.model_api import *


class ct_covered_connecticut(Variable):
    value_type = float
    entity = TaxUnit
    label = "Covered Connecticut Program premium assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "ct_covered_connecticut_eligible"
    reference = (
        "https://www.cga.ct.gov/2021/act/pa/pdf/2021PA-00002-R00SB-01202SS1-PA.pdf#page=22",
        "https://www.cga.ct.gov/2021/act/pa/pdf/2021PA-00002-R00SB-01202SS1-PA.pdf#page=24",
        "https://portal.ct.gov/dss/health-and-home-care/covered-connecticut-program",
    )
    documentation = (
        "Covered Connecticut pays the enrollee's residual benchmark silver-plan "
        "premium after the federal advance premium tax credit, driving the net "
        "premium to $0 for eligible enrollees at or below 175% of the federal "
        "poverty line. The premium tax credit's benchmark second-lowest-cost "
        "silver plan premium for the coverage family (aca_ptc_slcsp) proxies "
        "the benchmark plan and is annualized from its monthly definition; it "
        "leaves out an enrollee who is not eligible for the federal subsidies "
        "because they can be claimed on another return. The subsidy is additive on top of the federal APTC and is "
        "capped implicitly at the benchmark premium because the federal APTC "
        "never exceeds it, so the residual is never negative. The program also "
        "zeroes cost-sharing and adds dental and non-emergency medical "
        "transportation benefits, which form a separate benefits axis and are "
        "not modeled here. The subsidy is not counted as income for Connecticut "
        "personal income tax purposes under Public Act 21-2, Section 16(d), so "
        "it is not added to Connecticut adjusted gross income."
    )

    def formula(tax_unit, period, parameters):
        # The benchmark for the federal coverage family, a MONTH variable that
        # add() annualizes to match the YEAR-period aca_ptc. Public Act 21-2,
        # Section 16(b)(1), covers only people eligible for premium and
        # cost-sharing subsidies, so an enrollee outside the federal tax
        # family (one who can be claimed on another return) is left out.
        slcsp_annual = add(tax_unit, period, ["aca_ptc_slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Residual benchmark premium after the federal APTC. The max_(0, ...)
        # floor is defensive and redundant in the baseline, where aca_ptc never
        # exceeds the benchmark slcsp, but is retained for robustness.
        return max_(0, slcsp_annual - aca_ptc)
