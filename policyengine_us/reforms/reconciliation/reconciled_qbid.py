from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_qbid() -> Reform:
    class qbid_amount(Variable):
        value_type = float
        entity = Person
        label = "Per‑cap qualified business income deduction amount for each person"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
            "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
        )

    def formula(person, period, parameters):
        # --------------------------------------------------------------
        # Section 199A Qualified Business Income Deduction (QBID)
        # IRS Form 8995 / 8995-A
        # --------------------------------------------------------------
        p = parameters(period).gov.irs.deductions.qbi
    
        # --- Core inputs ---------------------------------------------
        # Form 8995 line 1 – Qualified business income (QBI)
        qbi = person("qualified_business_income", period)
    
        # SSTB check box (Form 8995 / 8995-A)
        is_sstb = person("business_is_sstb", period)
    
        # Form 8995 line 6 – Qualified REIT dividends and PTP income
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)
    
        # Optional: business-development-company dividends
        bdc_income = person("qualified_bdc_income", period)
    
        # Form 1040 line 15 – Taxable income before QBID
        taxable_income = person.tax_unit("taxable_income_less_qbid", period)
    
        # Reg. 1.199A-1(b)(3) – Net capital gain
        net_cap_gain = person.tax_unit("net_capital_gain", period)
    
        # Form 1040 filing-status check box
        filing_status = person.tax_unit("filing_status", period)
    
        # §199A(e)(2) thresholds
        threshold       = p.phase_out.start[filing_status]
        phase_in_range  = p.phase_out.length[filing_status]
    
        # --------------------------------------------------------------
        # 1. 20 % of QBI (§199A(a)(1))
        # --------------------------------------------------------------
        qbid_base = 0.20 * qbi
    
        # --------------------------------------------------------------
        # 2. Wage / UBIA limitation (§199A(b)(2))
        # --------------------------------------------------------------
        w2_wages      = person("w2_wages_from_qualified_business", period)
        ubia_property = person("unadjusted_basis_qualified_property", period)
    
        wage_limit  = 0.50 * w2_wages
        alt_limit   = 0.25 * w2_wages + 0.025 * ubia_property
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
    
        adj_qbid_base = qbid_base        * applicable_pct
        adj_cap       = wage_ubia_cap    * applicable_pct
    
        # --------------------------------------------------------------
        # 5. Apply wage/UBIA cap and phase-in reduction
        # --------------------------------------------------------------
        limited_deduction = min_(adj_qbid_base, adj_cap)
        excess_amount     = max_(0, adj_qbid_base - adj_cap)
        phased_deduction  = max_(0, adj_qbid_base - phase_in_pct * excess_amount)
    
        qbi_component = where(
            phase_in_pct == 0,
            adj_qbid_base,                      # below threshold
            where(
                is_sstb,
                limited_deduction,              # SSTB above threshold
                where(
                    phase_in_pct < 1,
                    phased_deduction,           # non-SSTB in phase-in band
                    limited_deduction           # fully phased-in
                )
            )
        )
    
        # --------------------------------------------------------------
        # 6. REIT / PTP (and optional BDC) component – always 20 %
        # --------------------------------------------------------------
        reit_ptp_bdc_base = reit_ptp_income + where(p.use_bdc_income, bdc_income, 0)
        reit_ptp_bdc_ded  = 0.20 * reit_ptp_bdc_base
    
        total_before_cap = qbi_component + reit_ptp_bdc_ded
    
        # --------------------------------------------------------------
        # 7. Overall income cap (§199A(a)(2))
        #     20 % * (taxable income – net capital gain)
        # --------------------------------------------------------------
        income_cap = 0.20 * max_(0, taxable_income - net_cap_gain)
    
        return min_(total_before_cap, income_cap)

    class reform(Reform):
        def apply(self):
            self.update_variable(qbid_amount)

    return reform


def create_reconciled_qbid_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_reconciled_qbid()

    p = parameters.gov.contrib.reconciliation.qbid

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_qbid()
    else:
        return None


reconciled_qbid = create_reconciled_qbid_reform(None, None, bypass=True)
