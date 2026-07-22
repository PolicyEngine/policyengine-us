from policyengine_us.model_api import *


class mt_taxable_social_security_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits for joint filers"
    defined_for = StateCode.MT
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.social_security.amount
        p_irs = parameters(period).gov.irs.social_security.taxability.rate
        # Joint filers run the Taxable Social Security Benefits Schedule once
        # in a single column, combining both spouses' lines 1-9 and applying
        # the joint base amounts once (Form 2, page 6).
        # line 1 total net SS amount
        social_security = add(tax_unit, period, ["social_security"])
        # line 2 SS multiplied by the base rate
        social_security_benefits_fraction = social_security * p_irs.base.benefit_cap
        # line 3: irs_gross_income - taxable_social_security
        gross_income = add(tax_unit, period, ["irs_gross_income"])
        taxable_ss = add(tax_unit, period, ["taxable_social_security"])
        reduced_gross_income = max_(gross_income - taxable_ss, 0)
        # line 5: tax exempt interest income
        tax_exempt_interest_income = add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )
        # line 6: Sum of line 2, 3, 4, 5
        income_increased_by_ss_and_interest = (
            social_security_benefits_fraction
            + reduced_gross_income
            + tax_exempt_interest_income
        )
        # line 7: Remove the student loans from the above the line deductions
        ald_less_student_loan = add(
            tax_unit, period, ["mt_applicable_ald_deductions"]
        ) - add(tax_unit, period, ["student_loan_interest_ald"])
        # line 8: Montana subtractions + ald
        subtractions = add(tax_unit, period, ["mt_subtractions"])
        increased_subtractions = subtractions + ald_less_student_loan
        # line 9: line 6 - line 8, if line 8 >= line 6, return 0
        income_reduced_by_subtractions = max_(
            0, income_increased_by_ss_and_interest - increased_subtractions
        )
        # line 10: joint base amount applied once
        filing_status = tax_unit("filing_status", period)
        threshold_amount = p.lower[filing_status]
        # line 11: line 9 - line 10
        income_reduced_by_subtractions_and_threshold = max_(
            0, income_reduced_by_subtractions - threshold_amount
        )
        # line 12: joint span applied once
        amount_lower = p.upper[filing_status] - p.lower[filing_status]
        # line 13: line 11 - line 12
        minimum_tax_threshold = max_(
            0, income_reduced_by_subtractions_and_threshold - amount_lower
        )
        # line 14 & 15
        capped_reduced_income = min_(
            income_reduced_by_subtractions_and_threshold, amount_lower
        )
        minimum_tax_threshold_fraction = capped_reduced_income * p_irs.base.excess
        # line 16
        smaller_fraction = min_(
            minimum_tax_threshold_fraction, social_security_benefits_fraction
        )
        # line 17 & 18: line_13 * 0.85 + line_16
        adjusted_tax_amount = (
            minimum_tax_threshold * p_irs.additional.benefit_cap + smaller_fraction
        )
        # line 19: line_1 * 0.85
        adjusted_taxable_amount = social_security * p_irs.additional.excess
        # line 20
        return min_(adjusted_taxable_amount, adjusted_tax_amount)
