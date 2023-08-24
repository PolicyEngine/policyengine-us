from policyengine_us.model_api import *


class co_social_security_subtraction_spouse(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado social security subtraction for spouse"
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
        if p.social_security_subtraction_available:
            person = tax_unit.members
            taxable_social_security = person("taxable_social_security", period)
            social_security_survivors = person(
                "social_security_survivors", period
            )
            age_spouse = tax_unit("age_spouse", period)
            younger_condition = age_spouse < p.younger.age
            older_condition = age_spouse >= p.older.age
            spouse_sss = tax_unit.max(
                social_security_survivors
                * person("is_tax_unit_spouse", period)
            )
            spouse_tss = tax_unit.max(
                taxable_social_security * person("is_tax_unit_spouse", period)
            )
            cap_older_amount = min_(spouse_tss, p.younger.max_amount)
            older_output = where(older_condition, spouse_tss, cap_older_amount)
            older_allowable = where(older_condition, spouse_tss, older_output)
            return where(
                younger_condition,
                spouse_sss,
                older_allowable,
            )
        return 0
