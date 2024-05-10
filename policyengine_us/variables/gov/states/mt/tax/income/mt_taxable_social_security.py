from policyengine_us.model_api import *


class mt_taxable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana taxable social security benefits"
    defined_for = StateCode.MT
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.social_security
        # Compute the amount based on the schedule in tax form.
        # line 1&2: 6a in tax form ?
        social_security = tax_unit("social_security", period)
        social_security_benefits_fraction = social_security * p.rate.lower
        # line 3 total_income - taxable_social_security
        # line 4: Additions Schedule line 15 - line 3  (0?)
        # line 5:
        tax_emempt_interest_income = tax_unit(
            "tax_exempt_interest_income", period
        )
        # line 6: line 2+3+4+5
        new_total_income = (
            social_security_benefits_fraction
            + tax_unit("total_income", period)
            - tax_unit("taxable_social_security", period)
            + tax_emempt_interest_income
        )
        us_ald_exclue_stduent_loan = tax_unit(
            "above_the_line_deductions", period
        ) - tax_unit("student_loan_interest", period)
        # line 8
        person = tax_unit.members
        increased_subtractions = (
            person("mt_subtractions", period) + us_ald_exclue_stduent_loan
        )
        # line 9: line 6 -line 8, if line 8 >= line 6, return 0
        remaining_income = max(0, new_total_income - increased_subtractions)
        # line 10: get amount based on filing status
        amount_higher = p.social_security.amount.higher[filing_status]
        # line 11: line 9 - line 10
        # line 12: get amount based on filing status
        amount_lower = p.social_security.amount.lower[filing_status]
        # lien 13: line 11 - line 12
        minimum_tax_threshold = max_(
            0, amount_higher - remaining_income - amount_lower
        )
        # line 14 & 15
        minimum_tax_threshold_fraction = (
            min_(amount_higher - remaining_income, amount_lower) * p.rate.lower
        )
        # line 16
        minimum_fraction = min_(
            minimum_tax_threshold_fraction, social_security_benefits_fraction
        )
        # line 17 & 18 ## line_13*p.rate2 + line_16
        adjusted_tax_amount = (
            minimum_tax_threshold * p.rate.higher + minimum_fraction
        )
        # line 19 ## line_1*p.rate2
        adjusted_taxable_amount = social_security * p.rate.higher
        # line 20
        lesser_of_taxable_amount = min_(
            adjusted_taxable_amount, adjusted_tax_amount
        )
        # line 11: line 9 - line 10, if line 10 >= line 9, return 0. Else, proceed line 12 through 20
        return select(
            amount_higher < remaining_income,
            lesser_of_taxable_amount,
            default=0,
        )
