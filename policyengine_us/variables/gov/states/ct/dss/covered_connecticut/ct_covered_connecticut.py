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
        # PDF pages 706-709 (and 155-157): Public Act 26-68, Sec. 462,
        # re-enacting C.G.S. 19a-754c. Subsection (b)(1) on page 706 (fully
        # subsidized premium coverage), (c) on page 708 (dental and
        # non-emergency medical transportation optional from January 1,
        # 2027) and (e) on page 709 (not income for the personal income
        # tax). Sec. 130 of the same act (effective July 1, 2026, pages
        # 155-157) re-enacts subsections (a) to (c) with the earlier text,
        # which keeps those services mandatory; the Office of Legislative
        # Research (2026-R-0094, page 10) reads Sec. 462's narrowing as the
        # law. The model values neither service, so the conflict changes no
        # result.
        "https://www.cga.ct.gov/2026/ACT/PA/PDF/2026PA-00068-R00SB-00001-PA.PDF#page=706",
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
        "pays cost-sharing subsidies, which are not modeled here. It has "
        "provided dental and non-emergency medical transportation services; "
        "from January 1, 2027, C.G.S. 19a-754c(c), as amended by Public Act "
        "26-68, Section 462, makes those services optional for the Department "
        "of Social Services. The model does not value them in any year. The "
        "benefits and subsidies are not counted as income for Connecticut "
        "personal income tax purposes (C.G.S. 19a-754c(e), formerly Public Act "
        "21-2, Section 16(d)), so they are not added to Connecticut adjusted "
        "gross income."
    )

    def formula(tax_unit, period, parameters):
        # The benchmark for the federal coverage family, a MONTH variable that
        # add() annualizes to match the YEAR-period aca_ptc. C.G.S.
        # 19a-754c(b)(1) (Public Act 21-2, Section 16(b)(1), as amended by
        # Public Act 26-68, Section 462) covers only people eligible for
        # premium and cost-sharing subsidies, so an enrollee outside the
        # federal tax family (one who can be claimed on another return) is
        # left out.
        slcsp_annual = add(tax_unit, period, ["aca_ptc_slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Residual benchmark premium after the federal APTC. The max_(0, ...)
        # floor is defensive and redundant in the baseline, where aca_ptc never
        # exceeds the benchmark slcsp, but is retained for robustness.
        return max_(0, slcsp_annual - aca_ptc)
