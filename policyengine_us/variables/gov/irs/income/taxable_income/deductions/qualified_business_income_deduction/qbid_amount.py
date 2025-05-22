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
        
        # Basic inputs
        qbi = person("qualified_business_income", period)
        is_sstb = person("business_is_sstb", period)
        
        # REIT, PTP income (not subject to W-2/property limitations or SSTB phase-out)
        reit_ptp_income = person("qualified_reit_and_ptp_income", period)
        reit_ptp_deduction = p.max.rate * reit_ptp_income  # Always 20% with no limitations
        
        # Income and threshold determination
        taxinc_less_qbid = person.tax_unit("taxable_income_less_qbid", period)
        filing_status = person.tax_unit("filing_status", period)
        po_start = p.phase_out.start[filing_status]
        po_length = p.phase_out.length[filing_status]
        
        # Check if we're in the phase-out range or above
        above_threshold = taxinc_less_qbid > po_start
        in_phase_out_range = (taxinc_less_qbid > po_start) & (taxinc_less_qbid <= (po_start + po_length))
        fully_phased_out = taxinc_less_qbid > (po_start + po_length)
        
        # BELOW THRESHOLD: Simple 20% calculation, no limitations
        below_threshold_deduction = p.max.rate * qbi
        
        # ABOVE THRESHOLD: Apply W-2/property limitations and SSTB phase-out
        
        # W-2 wage and property limitations
        w2_wages = person("w2_wages_from_qualified_business", period)
        b_property = person("unadjusted_basis_qualified_property", period)
        
        wage_cap = w2_wages * p.max.w2_wages.rate  # 50% of W-2 wages
        alt_cap = (
            w2_wages * p.max.w2_wages.alt_rate  # 25% of W-2 wages
            + b_property * p.max.business_property.rate  # 2.5% of property
        )
        wage_property_cap = max_(wage_cap, alt_cap)
        
        # SSTB phase-out calculation
        # For SSTBs: QBI and wage/property caps are gradually reduced to zero
        # For non-SSTBs: QBI is subject to wage/property caps but no phase-out
        
        phase_out_percentage = where(
            in_phase_out_range,
            (taxinc_less_qbid - po_start) / po_length,
            where(fully_phased_out, 1.0, 0.0)
        )
        
        # SSTB adjustments: reduce QBI and caps by phase-out percentage
        sstb_qbi_reduction = where(is_sstb, phase_out_percentage, 0.0)
        adjusted_qbi = qbi * (1 - sstb_qbi_reduction)
        adjusted_wage_property_cap = wage_property_cap * (1 - sstb_qbi_reduction)
        
        # Calculate 20% of adjusted QBI
        qbi_20_percent = p.max.rate * adjusted_qbi
        
        # Apply wage/property limitation
        above_threshold_deduction = min_(qbi_20_percent, adjusted_wage_property_cap)
        
        # For taxpayers in phase-out range, there's also a second calculation
        # that phases out the excess of QBI over the wage/property cap
        excess_qbi_over_cap = max_(0, qbi_20_percent - adjusted_wage_property_cap)
        phase_out_reduction = phase_out_percentage * excess_qbi_over_cap
        alternative_calculation = max_(0, qbi_20_percent - phase_out_reduction)
        
        # Take the greater of the two calculations when in phase-out range
        above_threshold_deduction = where(
            in_phase_out_range,
            max_(above_threshold_deduction, alternative_calculation),
            above_threshold_deduction
        )
        
        # Select appropriate calculation based on income level
        qbi_deduction = where(
            above_threshold,
            above_threshold_deduction,
            below_threshold_deduction
        )
        
        # Add REIT/PTP deduction (never limited)
        total_deduction = qbi_deduction + reit_ptp_deduction
        
        # Final limitation: cannot exceed 20% of taxable income before QBI deduction
        taxable_income_cap = p.max.rate * taxinc_less_qbid
        
        return min_(total_deduction, taxable_income_cap)
