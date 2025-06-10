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
        # --------------------------------------------------------------
        # Section 199A Qualified Business Income Deduction (QBID)
        # IRS Form 8995 / 8995-A (TCJA final law)
        # --------------------------------------------------------------
        p = parameters(period).gov.irs.deductions.qbi
    
        # --- Core inputs ---------------------------------------------
        # Form 8995 line 1 – Qualified business income (QBI)
        qbi = person("qualified_business_income", period)
    
        # Form 8995-A Part I – W-2 wages from the trade or business
        w2_wages = person("w2_wages_from_qualified_business", period)
    
        # Form 8995-A Part I – Unadjusted basis immediately after acquisition (UBIA)
        ubia_property = person("unadjusted_basis_qualified_property", period)
    
        # SSTB check box (Form 8995 / 8995-A)
        is_sstb = person("business_is_sstb", period)
    
        # Form 8995 line 6 – Qualified REIT dividends and PTP income
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)
    
        # Form 1040 line 15 – Taxable income before QBID
        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
    
        # Reg. 1.199A-1(b)(3) – Net capital gain (incl. qualified dividends)
        net_cap_gain = person.tax_unit("net_capital_gain", period)
    
        # Form 1040 filing status
        filing_status = person.tax_unit("filing_status", period)
    
        # §199A(e)(2) – Threshold and phase-in range
        threshold      = p.phase_out.start[filing_status]
        phase_in_range = p.phase_out.length[filing_status]
    
        # --------------------------------------------------------------
        # 1. 20 % of QBI (§199A(a)(1))
        # --------------------------------------------------------------
        qbid_max = 0.20 * qbi
    
        # --------------------------------------------------------------
        # 2. Wage / UBIA limitation (§199A(b)(2))
        # --------------------------------------------------------------
        wage_limit = 0.50 * w2_wages
        alt_limit  = 0.25 * w2_wages + 0.025 * ubia_property
        wage_ubia_cap = max_(wage_limit, alt_limit)
    
        # --------------------------------------------------------------
        # 3. Phase-in percentage (§199A(b)(3)(B))
        # --------------------------------------------------------------
        over_threshold = max_(0, taxable_income - threshold)
        phase_in_pct   = min_(1, over_threshold / phase_in_range)
    
        # --------------------------------------------------------------
        # 4. SSTB applicable percentage (Reg. 1.199A-5)
        # --------------------------------------------------------------
        applicable_pct = where(is_sstb, 1 - phase_in_pct, 1)
    
        adj_qbid_max = qbid_max      * applicable_pct
        adj_cap      = wage_ubia_cap * applicable_pct
    
        # --------------------------------------------------------------
        # 5. Phase-in deduction calculation (Worksheet 12-A logic)
        # --------------------------------------------------------------
        limited_deduction = min_(adj_qbid_max, adj_cap)
        excess_amount     = max_(0, adj_qbid_max - adj_cap)
        phased_deduction  = max_(0, adj_qbid_max - phase_in_pct * excess_amount)
    
        deduction_pre_cap = where(
            phase_in_pct == 0,              # Below threshold
            adj_qbid_max,
            where(
                is_sstb,                    # SSTB above threshold
                limited_deduction,
                where(                      # Non-SSTB
                    phase_in_pct < 1,
                    phased_deduction,       # In the phase-in band
                    limited_deduction       # Fully phased-in
                )
            )
        )
    
        # --------------------------------------------------------------
        # 6. REIT / PTP component – always 20 % (§199A(c)(1)(B))
        # --------------------------------------------------------------
        reit_ptp_deduction = 0.20 * reit_ptp_income
    
        total_before_cap = deduction_pre_cap + reit_ptp_deduction
    
        # --------------------------------------------------------------
        # 7. Overall income cap (§199A(a)(2))
        #     20 % × (taxable income – net capital gain)
        # --------------------------------------------------------------
        income_cap = 0.20 * max_(0, taxable_income - net_cap_gain)
    
        return min_(total_before_cap, income_cap)
