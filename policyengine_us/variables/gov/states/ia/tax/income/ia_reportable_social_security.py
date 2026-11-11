from policyengine_us.model_api import *


class ia_reportable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa reportable social security benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "IA 1040 step 4, from the reportable Social Security benefits "
        "worksheet. Line 1 takes the head's and spouse's benefits from Forms "
        "SSA-1099 only. Line 7 adds half of those benefits, half of the tier "
        "1 railroad retirement benefits from Form RRB-1099 (line 4) and the "
        "other income on Form 1040 without line 6b."
    )
    reference = (
        # 2021 IA 1040 instructions, step 4 worksheet, lines 1-13.
        "https://revenue.iowa.gov/media/2650/download?inline#page=11",
        # 2022 IA 1040 instructions, step 4 worksheet, lines 1-13.
        "https://revenue.iowa.gov/media/2721/download?inline#page=10",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.reportable_social_security
        filing_status = tax_unit("filing_status", period)
        # Line 1: box 5 of the head's and spouse's Forms SSA-1099. A
        # dependent's benefits go on the dependent's own return.
        title_ii = tax_unit("tax_unit_social_security_for_taxability", period)
        # Line 4: box 5 of Form RRB-1099, the net social security equivalent
        # benefit.
        tier_1 = tax_unit(
            "tax_unit_railroad_social_security_equivalent_benefits_for_taxability",
            period,
        )
        # Lines 3 and 8: federal AGI without Form 1040 line 6b (the taxable
        # title II and tier 1 benefits). Line 8 counts Schedule 1 lines 11 to
        # 20, 23 and the other adjustments, so not the student loan interest
        # deduction on line 21.
        agi = tax_unit("adjusted_gross_income", period)
        taxable_benefits = tax_unit("tax_unit_taxable_section_86_benefits", period)
        student_loan_interest = tax_unit_non_dep_add(
            tax_unit, period, ["student_loan_interest_ald"]
        )
        # Line 6: tax-exempt interest, Form 1040 line 2a.
        tax_exempt_interest = tax_unit_non_dep_add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )
        # Lines 2, 4 and 7-9.
        income = (
            agi
            - taxable_benefits
            + student_loan_interest
            + tax_exempt_interest
            + p.fraction * (title_ii + tier_1)
        )
        # Lines 10-12.
        deduction = p.deduction[filing_status]
        excess = max_(0, income - deduction)
        # Line 13: the smaller of line 2 and line 12.
        return min_(p.fraction * title_ii, p.fraction * excess)
