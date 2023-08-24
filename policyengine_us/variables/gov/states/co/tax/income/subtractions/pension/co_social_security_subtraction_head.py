from policyengine_us.model_api import *


class co_social_security_subtraction_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado social security subtraction for head"
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
            p = parameters(
                period
            ).gov.states.co.tax.income.subtractions.pension
            person = tax_unit.members
            taxable_social_security = person("taxable_social_security", period)
            social_security_survivors = person(
                "social_security_survivors", period
            )
            age_head = tax_unit("age_head", period)
            younger_condition = age_head < p.younger.age
            older_condition = age_head >= p.older.age
            head_sss = tax_unit.max(
                social_security_survivors * person("is_tax_unit_head", period)
            )
            head_tss = tax_unit.max(
                taxable_social_security * person("is_tax_unit_head", period)
            )
            cap_older_amount = min_(head_tss, p.younger.max_amount)
            older_output = where(older_condition, head_tss, cap_older_amount)
            older_allowable = where(older_condition, head_tss, older_output)
            return where(younger_condition, head_sss, older_allowable)
        return 0
