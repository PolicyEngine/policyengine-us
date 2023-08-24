from policyengine_us.model_api import *


class co_pension_subtraction_spouse(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado pension and annuity subtraction for spouse"
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
        co_social_security_subtraction_spouse = tax_unit(
            "co_social_security_subtraction_spouse", period
        )
        age_spouse = tax_unit("age_spouse", period)
        younger_condition = age_spouse < p.younger.age
        older_condition = age_spouse >= p.older.age
        pension_survivors = tax_unit.max(
            pension_survivors * person("is_tax_unit_spouse", period)
        )
        spouse_tpi = tax_unit.max(
            taxable_pension_income * person("is_tax_unit_spouse", period)
        )
        # same as co_pension_head
        younger_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_spouse, 0
        )
        younger_spouse_output = min_(younger_allowable, pension_survivors)
        older_allowable = max_(
            p.older.max_amount - co_social_security_subtraction_spouse, 0
        )
        older_spouse_output = min_(older_allowable, spouse_tpi)
        intermediate_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_spouse, 0
        )
        intermediate_spouse_output = min_(intermediate_allowable, spouse_tpi)
        return where(
            younger_condition,
            younger_spouse_output,
            where(
                older_condition,
                older_spouse_output,
                intermediate_spouse_output,
            ),
        )
