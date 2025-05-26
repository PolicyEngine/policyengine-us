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
        qbi = person("qualified_business_income", period)
        w2_wages = person("w2_wages_from_qualified_business", period)
        ubia_property = person("unadjusted_basis_qualified_property", period)
        is_sstb = person("business_is_sstb", period)
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)

        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)

        threshold = p.phase_out.start[filing_status]
        phase_in_range = p.phase_out.length[filing_status]

        # 2. 20 % of QBI ---------------------------------------------------------
        qbi_twenty = p.max.rate * qbi

        # 3. Wage / UBIA limitation ---------------------------------------------
        wage_limit = p.max.w2_wages.rate * w2_wages  # 50 % of W‑2 wages
        alt_limit = (
            p.max.w2_wages.alt_rate * w2_wages  # 25 % of W‑2 wages
            + p.max.business_property.rate * ubia_property  # 2.5 % of UBIA
        )
        wage_ubia_cap = max_(wage_limit, alt_limit)

        # 4. Phase‑in percentage (§199A(b)(3)(B)) -------------------------------
        over_threshold = max_(0, taxable_income - threshold)
        phase_in_pct = min_(1, over_threshold / phase_in_range)

        # 5. Applicable percentage for SSTBs ------------------------------------
        applicable_pct = where(is_sstb, 1 - phase_in_pct, 1)

        adj_qbi_twenty = qbi_twenty * applicable_pct
        adj_cap = wage_ubia_cap * applicable_pct

        limited_deduction = min_(adj_qbi_twenty, adj_cap)
        excess = max_(0, adj_qbi_twenty - adj_cap)
        phased_deduction = max_(0, adj_qbi_twenty - phase_in_pct * excess)

        deduction_pre_cap = where(
            phase_in_pct == 0,
            adj_qbi_twenty,  # Below threshold: wage/UBIA limit does not apply.
            where(
                phase_in_pct < 1,
                max_(limited_deduction, phased_deduction),  # Inside phase‑in band.
                limited_deduction,  # Over the band: limitation fully applies.
            ),
        )

        # 6. REIT / PTP component (always 20 %) ---------------------------------
        reit_ptp_deduction = p.max.rate * reit_ptp_income
        total_before_income_cap = deduction_pre_cap + reit_ptp_deduction

        # 7. Overall 20 % taxable‑income ceiling (§199A(a)(2)) ------------------
        income_cap = p.max.rate * taxable_income
        return min_(total_before_income_cap, income_cap)
