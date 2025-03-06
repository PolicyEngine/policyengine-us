from policyengine_us.model_api import *


class ms_retirement_income_exemption(Variable):
    value_type = float
    entity = Person
    label = "Mississippi retirement income exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-15/"  # (4)(k)
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        excluded_income = add(
            person,
            period,
            [
                "taxable_social_security",
                "taxable_pension_income",
            ],
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * excluded_income
