from policyengine_us.model_api import *


class mt_taxable_social_security(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable social security benefits"
    defined_for = StateCode.MT
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.social_security.amount
        p_irs = parameters(period).gov.irs.social_security.taxability.rate
        # Compute the amount based on the schedule in Montana tax form.
        # line 1 total net SS amount
        social_security = person("social_security", period)
        # Line 2 SS multiplied by the base rate
        social_security_benefits_fraction = social_security * p_irs.base
        # line 3: irs_gross_income - taxable_social_security
        taxable_ss = person("taxable_social_security", period)
        gross_income = person("irs_gross_income", period)
        reduced_gross_income = max_(gross_income - taxable_ss, 0)
        # line 4: Additions Schedule line 15 - Additions Schedule line 3
        # Interest and mutual fund dividends from state, county, or municipal bonds
        # from other states - not included
        # line 5: tax exempt interest income
        tax_exempt_interest_income = person(
            "tax_exempt_interest_income", period
        )
        # line 6: Sum of line 2, 3, 4, 5
        income_increased_by_ss_and_interest = (
            social_security_benefits_fraction
            + reduced_gross_income
            + tax_exempt_interest_income
        )
        # line 7: Remove the student loans from the above the line deductions
        ald_less_student_loan = person(
            "mt_applicable_ald_deductions", period
        ) - person("student_loan_interest_ald", period)
        # Line 8 - Montana subtractions + ald
        subtractions = person("mt_subtractions", period)
        increased_subtractions = subtractions + ald_less_student_loan
        # line 9: line 6 -line 8, if line 8 >= line 6, return 0
        income_reduced_by_subtractions = max_(
            0, income_increased_by_ss_and_interest - increased_subtractions
        )
        # line 10: get amount based on filing status
        filing_status = person.tax_unit("filing_status", period)
        threshold_amount = p.lower[filing_status]
        # line 11: line 9 - line 10 (income_reduced_by_subtractions - threshold_amount)
        income_reduced_by_subtractions_and_threshold = max_(
            0, income_reduced_by_subtractions - threshold_amount
        )
        # line 12: get amount based on filing status
        amount_lower = p.upper[filing_status] - p.lower[filing_status]
        # lien 13: line 11 - line 12
        minimum_tax_threshold = max_(
            0, income_reduced_by_subtractions_and_threshold - amount_lower
        )
        # line 14 & 15
        capped_reduced_income = min_(
            income_reduced_by_subtractions_and_threshold, amount_lower
        )
        minimum_tax_threshold_fraction = capped_reduced_income * p_irs.base
        # line 16
        smaller_fraction = min_(
            minimum_tax_threshold_fraction, social_security_benefits_fraction
        )
        # line 17 & 18 ## line_13*0.85 + line_16
        adjusted_tax_amount = (
            minimum_tax_threshold * p_irs.additional + smaller_fraction
        )
        # line 19 ## line_1*0.85
        adjusted_taxable_amount = social_security * p_irs.additional
        # line 20
        return min_(adjusted_taxable_amount, adjusted_tax_amount)
