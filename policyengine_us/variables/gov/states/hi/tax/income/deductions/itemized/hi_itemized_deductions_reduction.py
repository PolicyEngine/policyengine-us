from policyengine_us.model_api import *


class hi_itemized_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deductions reduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # HRS 235-2.4 keeps IRC section 68 operative with the 2009 thresholds;
        # Act 35, SLH 2026 keeps it "in the form that it existed as of
        # December 31, 2024" for taxable years beginning after 2025.
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=18",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partI-sec68.htm",
        # Total Itemized Deductions Worksheet, lines 2 to 10.
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        total_deductions = tax_unit("hi_total_itemized_deductions", period)
        # Lines 2 to 5: 80% of the deductions other than medical expenses,
        # investment interest and casualty losses. If those deductions are not
        # less than the total, the deduction is not limited.
        excluded_deductions = add(tax_unit, period, p.limitation.excluded_deductions)
        limited_deductions = max_(0, total_deductions - excluded_deductions)
        deduction_based_reduction = (
            limited_deductions * p.limitation.itemized_deduction_rate
        )
        # Lines 6 to 9: 3% of Hawaii AGI above the threshold. If Hawaii AGI is
        # not above the threshold, the deduction is not limited.
        hi_agi = tax_unit("hi_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_excess = max_(0, hi_agi - p.threshold.reduction[filing_status])
        agi_based_reduction = agi_excess * p.limitation.agi_rate
        # Line 10: the smaller of the two.
        return min_(deduction_based_reduction, agi_based_reduction)
