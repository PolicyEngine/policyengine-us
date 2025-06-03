from policyengine_us.model_api import *


class qbid_amount(Variable):
    value_type = float
    entity = Person
    label = (
        "Per-cap qualified business income deduction amount for each person"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
    )

    def formula(person, period, parameters):

        p = parameters(period).gov.irs.deductions.qbi

        # 1. Core inputs ---------------------------------------------------------
        # IRS Form 8995, line 1 (qualified business income)
        qbi = person("qualified_business_income", period)
        # W‑2 wages for the trade or business (Form 8995‑A, Part I)
        w2_wages = person("w2_wages_from_qualified_business", period)
        # Unadjusted basis immediately after acquisition (UBIA)
        # (Form 8995‑A, Part I)
        ubia_property = person("unadjusted_basis_qualified_property", period)
        # Specified service trade or business check box on Form 8995/8995‑A
        is_sstb = person("business_is_sstb", period)
        # Form 8995, line 6 (REIT/PTP income)
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)

        # Form 1040, line 15 (taxable income) before QBID
        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
        # Form 1040, filing status check box
        filing_status = person.tax_unit("filing_status", period)

        threshold = p.phase_out.start[filing_status]
        phase_in_range = p.phase_out.length[filing_status]

        # 2. 20 % of QBI ---------------------------------------------------------
        qbid_max = p.max.rate * qbi
        # 20% of qualified business income (Worksheet 12‑A)

        # 3. Wage / UBIA limitation ---------------------------------------------
        wage_limit = p.max.w2_wages.rate * w2_wages  # 50 % of W‑2 wages
        # Worksheet 12‑A: 50% of W‑2 wages
        alt_limit = (
            p.max.w2_wages.alt_rate * w2_wages  # 25 % of W‑2 wages
            + p.max.business_property.rate * ubia_property  # 2.5 % of UBIA
        )
        # Worksheet 12‑A: 25% of W‑2 wages plus 2.5% of UBIA
        wage_ubia_cap = max_(wage_limit, alt_limit)
        # Worksheet 12‑A: wage/property limitation

        # 4. Phase‑in percentage (§199A(b)(3)(B)) -------------------------------
        over_threshold = max_(0, taxable_income - threshold)
        phase_in_pct = min_(1, over_threshold / phase_in_range)
        # Portion of income within the phase‑in range (Worksheet 12‑A)

        # 5. Applicable percentage for SSTBs ------------------------------------
        applicable_pct = where(is_sstb, 1 - phase_in_pct, 1)

        adj_qbid_max = qbid_max * applicable_pct
        adj_cap = wage_ubia_cap * applicable_pct
        # Worksheet 12‑A: apply SSTB percentage

        limited_deduction = min_(adj_qbid_max, adj_cap)
        excess = max_(0, adj_qbid_max - adj_cap)
        phased_deduction = max_(0, adj_qbid_max - phase_in_pct * excess)
        # Worksheet 12‑A: phase‑in calculation

        deduction_pre_cap = where(
            phase_in_pct == 0,
            adj_qbid_max,  # Below threshold: wage/UBIA limit does not apply.
            where(
                phase_in_pct < 1,
                max_(
                    limited_deduction, phased_deduction
                ),  # Inside phase‑in band.
                limited_deduction,  # Over the band: limitation fully applies.
            ),
        )
        # Worksheet 12‑A: deduction before taxable‑income cap

        # 6. REIT / PTP component (always 20 %) ---------------------------------
        reit_ptp_deduction = p.max.rate * reit_ptp_income
        # Worksheet 12‑A: REIT/PTP component
        total_before_income_cap = deduction_pre_cap + reit_ptp_deduction

        # 7. Overall 20 % taxable‑income ceiling (§199A(a)(2)) ------------------
        income_cap = p.max.rate * taxable_income
        # Worksheet 12‑A: taxable‑income limitation
        return min_(total_before_income_cap, income_cap)
