from policyengine_us.model_api import *


class co_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado military retirement subtraction"
    defined_for = StateCode.CO
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(4)(y)(I)
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.military_retirement
        person = tax_unit.members
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        age_eligible = age < p.age_threshold
        eligible = head_or_spouse * age_eligible
        military_retirement_pay = person("military_retirement_pay", period)
        capped_military_retirement_pay = min_(
            military_retirement_pay * eligible, p.max_amount
        )
        return tax_unit.sum(capped_military_retirement_pay)
