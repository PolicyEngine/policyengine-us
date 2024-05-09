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
        # line 1&2: 6a in tax form ?
        social_security_benefit = tax_unit("social_security",period)
        fraction_of_social_security_benefit= social_security_benefit*p.rate1
        # line 3
        tax_unit("total_income",period) - tax_unit("taxable_social_security",period)
        # line 4: Additions Schedule line 15 - line 3 
        0
        # line 5: 
        tax_emempt_interest_income = tax_unit("tax_exempt_interest_income",period) 
        # line 6: line 2+3+4+5
        line_6 = fraction_of_social_security_benefit + tax_unit("total_income",period) - tax_unit("taxable_social_security",period) +tax_emempt_interest_income
        us_ald = tax_unit("above_the_line_deductions",period) - tax_unit("student_loan_interest", period) 
        # line 8
        person = tax_unit.members
        line_8 = person("mt_subtractions", period) + us_ald
        # line 9: line 8 -line 6, if line 8 >= line 6, return 0 
        line_9 = max(0, line_8 - line_6)
        # line 10: get amount based on filing status
        amount_1 = p.social_security.amount1[filing_status] 
        # line 12: get amount based on filing status
        amount_2 = p.social_security.amount2[filing_status]
        # lien 13: line 11 - line 12 
        line_13 = max(0,amount_1 - line_9 - amount_2)
        # line 14 & 15
        line_15 = min(amount_1 - line_9,amount_2)*p.rate1
        # line 16
        line_16 = min(line_15,fraction_of_social_security_benefit)
        # line 17 & 18 ## line_13*p.rate2 + line_16
        # line 19 ## social_security_benefit*p.rate2
        # line 20 
        lesser_of_18_or_19 = min(social_security_benefit*p.rate2, line_13*p.rate2 + line_16)
        # line 11: line 10 - line 9, if line 10 >= line 9, return 0 
        return select(
                amount_1 < line_9,
                lesser_of_18_or_19,
            default=0,
        )
        