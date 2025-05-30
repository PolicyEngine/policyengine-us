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
            p = parameters(period).gov.irs.deductions.qbi
            p_ref = parameters(period).gov.contrib.reconciliation.qbid

            # 1. Core inputs ----------------------------------------------------
            # Form 8995, line 1 (qualified business income)
            qbi = person("qualified_business_income", period)
            # Specified service trade or business check box on Form 8995/8995-A
            is_sstb = person("business_is_sstb", period)

            # Form 8995, line 6 (REIT/PTP income)
            reit_ptp_income = person("qualified_reit_and_ptp_income", period)
            # Income from business development companies (not on current forms)
            bdc_income = person("qualified_bdc_income", period)

            # Form 1040, line 15 (taxable income) before QBID
            taxable_income = person.tax_unit(
                "taxable_income_less_qbid", period
            )
            # Form 1040, filing status check box
            filing_status = person.tax_unit("filing_status", period)

            threshold = p.phase_out.start[filing_status]  # §199A(e)(2)
            phase_in_rate = p_ref.phase_out_rate  # 75 % "phase-in" rate

            # 2. 23 % of total QBI ---------------------------------------------
            qbid_max = p.max.rate * qbi

            # 3. Wage / UBIA limitation (non-SSTB only) ------------------------
            # W-2 wages for the trade or business (Form 8995-A, Part I)
            w2_wages = person("w2_wages_from_qualified_business", period)
            # Unadjusted basis immediately after acquisition (UBIA)
            # (Form 8995-A, Part I)
            ubia_property = person(
                "unadjusted_basis_qualified_property", period
            )

            qbi_non_sstb = (1 - is_sstb) * qbi
            w2_wages_non_sstb = (1 - is_sstb) * w2_wages
            ubia_property_non_sstb = (1 - is_sstb) * ubia_property

            wage_limit = p.max.w2_wages.rate * w2_wages_non_sstb  # 50 % wages
            alt_limit = (
                p.max.w2_wages.alt_rate * w2_wages_non_sstb  # 25 % wages
                + p.max.business_property.rate
                * ubia_property_non_sstb  # 2.5 % UBIA
            )
            wage_ubia_cap = max_(wage_limit, alt_limit)

            step1_uncapped = p.max.rate * qbi_non_sstb
            step1_deduction = min_(step1_uncapped, wage_ubia_cap)

            # 4. Limitation phase-in amount (75 % × excess) --------------------
            excess_income = max_(0, taxable_income - threshold)
            phase_in_amount = phase_in_rate * excess_income

            step2_deduction = max_(0, qbid_max - phase_in_amount)

            # 5. QBI component: greater of Step 1 or Step 2 --------------------
            qbi_component = max_(step1_deduction, step2_deduction)

            # 6. REIT, PTP, and optional BDC component (always 23 %) -----------
            reit_ptp_bdc_base = reit_ptp_income + where(
                p_ref.use_bdc_income,
                bdc_income,
                0,
            )
            reit_ptp_bdc_deduction = p.max.rate * reit_ptp_bdc_base

            total_before_income_cap = qbi_component + reit_ptp_bdc_deduction

            # 7. Overall 23 % taxable-income ceiling (§199A(a)(2)) -------------
            income_cap = p.max.rate * taxable_income

            return min_(total_before_income_cap, income_cap)

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
