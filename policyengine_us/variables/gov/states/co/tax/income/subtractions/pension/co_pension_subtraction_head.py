from policyengine_us.model_api import *


class co_pension_subtraction_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado pension and annuity subtraction for head"
    defined_for = StateCode.CO
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/"
        # C.R.S. 39-22-104(4)(g)(III)
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        person = tax_unit.members
        taxable_pension_income = person("taxable_pension_income", period)
        pension_survivors = person("pension_survivors", period)
        co_social_security_subtraction_head = tax_unit(
            "co_social_security_subtraction_head", period
        )
        age_head = tax_unit("age_head", period)
        younger_condition = age_head < p.younger.age
        older_condition = age_head >= p.older.age
        pension_survivors = tax_unit.max(
            pension_survivors * person("is_tax_unit_head", period)
        )
        head_tpi = tax_unit.max(
            taxable_pension_income * person("is_tax_unit_head", period)
        )
        # subtract $20,000 minus any amount entered on line 3(co_social_security_subtraction_head),
        # or pension_survivors, whichever is smaller.
        # if the amount on line 3 of this form is greater than $20,000, you may not claim any subtraction.
        younger_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_head, 0
        )
        younger_head_output = min_(younger_allowable, pension_survivors)
        # subtract $24,000 minus any amount entered on line 3(co_social_security_subtraction_head),
        # or taxable_pension_income, whichever is smaller.
        # if the amount on line 3 of this form is greater than $24,000, you may not claim any subtraction.
        older_allowable = max_(
            p.older.max_amount - co_social_security_subtraction_head, 0
        )
        older_head_output = min_(older_allowable, head_tpi)
        # subtract $20,000 minus any amount entered on line 3(co_social_security_subtraction_head),
        # or taxable_pension_income, whichever is smaller.
        # if the amount on line 3 of this form is greater than $20,000, you may not claim any subtraction.
        intermediate_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_head, 0
        )
        intermediate_head_output = min_(intermediate_allowable, head_tpi)
        
        return where(
            younger_condition,
            younger_head_output,
            where(
                older_condition,
                older_head_output,
                intermediate_head_output,
            ),
        )
