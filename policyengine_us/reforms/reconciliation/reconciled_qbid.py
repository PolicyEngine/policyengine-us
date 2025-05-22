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
            p = parameters(period).gov.irs.deductions
            p_ref = parameters(period).gov.contrib.reconciliation.qbid
            
            # Basic inputs
            qbi = person("qualified_business_income", period)
            is_sstb = person("business_is_sstb", period)  # Boolean indicator
            
            # Split QBI based on SSTB status (simplified: all or none)
            qbi_sstb = where(is_sstb, qbi, 0)
            qbi_non_sstb = where(is_sstb, 0, qbi)
            
            # REIT, PTP, and BDC income (not subject to any limitations)
            reit_ptp_income = person("qualified_reit_and_ptp_income", period)
            bdc_income = person("qualified_bdc_income", period)

            if p_ref.use_bdc_income:
                reit_ptp_bdc_deduction = p.qbi.max.rate * (reit_ptp_income + bdc_income)
            else:
                reit_ptp_bdc_deduction = p.qbi.max.rate * reit_ptp_income
            
            # Income and threshold determination
            taxinc_less_qbid = person.tax_unit("taxable_income_less_qbid", period)
            filing_status = person.tax_unit("filing_status", period)
            threshold = p.qbi.phase_out.start[filing_status]
            
            # Check if above threshold
            above_threshold = taxinc_less_qbid > threshold
            
            # BELOW THRESHOLD: Simple calculation (no limitations)
            below_threshold_qbi_deduction = p.qbi.max.rate * qbi  # 23% of all QBI
            below_threshold_total = below_threshold_qbi_deduction + reit_ptp_bdc_deduction
            
            # ABOVE THRESHOLD: Two-step process
            
            # STEP 1: Non-SSTB businesses only, with W-2/property limitations
            # (SSTBs get $0 in Step 1 because they're not "qualified trades or businesses" 
            # under IRC 199A(d)(1)(A) for limitation purposes)
            
            w2_wages = person("w2_wages_from_qualified_business", period)
            b_property = person("unadjusted_basis_qualified_property", period)
            
            # W-2 wage and property limitations (applied to non-SSTB only)
            wage_cap = w2_wages * p.qbi.max.w2_wages.rate  # 50% of W-2 wages
            alt_cap = (
                w2_wages * p.qbi.max.w2_wages.alt_rate  # 25% of W-2 wages
                + b_property * p.qbi.max.business_property.rate  # 2.5% of property
            )
            wage_property_cap = max_(wage_cap, alt_cap)
            
            # Step 1 calculation: 23% of non-SSTB QBI, limited by wage/property cap
            step1_uncapped = p.qbi.max.rate * qbi_non_sstb  # 23% of non-SSTB QBI
            step1_deduction = min_(step1_uncapped, wage_property_cap)
            
            # STEP 2: All QBI (including SSTB), reduced by phase-out
            phase_out_rate = p_ref.phase_out_rate  # 75%
            excess_income = max_(0, taxinc_less_qbid - threshold)
            reduction_amount = phase_out_rate * excess_income
            
            # Step 2 calculation: 23% of ALL QBI, reduced by 75% of excess income
            step2_uncapped = p.qbi.max.rate * qbi  # 23% of total QBI (SSTB + non-SSTB)
            step2_deduction = max_(0, step2_uncapped - reduction_amount)
            
            # FINAL CALCULATION: Take the GREATER of Step 1 and Step 2
            above_threshold_qbi_deduction = max_(step1_deduction, step2_deduction)
            
            # Add REIT, PTP, and BDC income (not subject to any limitations)
            above_threshold_total = above_threshold_qbi_deduction + reit_ptp_bdc_deduction
            
            # Use where() to select between below and above threshold calculations
            total_deduction = where(
                above_threshold,
                above_threshold_total,
                below_threshold_total
            )
            
            return total_deduction


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
