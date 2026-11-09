from policyengine_us.model_api import *


class va_military_benefit_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia military benefit subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.02/",
        "https://www.tax.virginia.gov/military-benefits-faq",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.military_benefit
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        military_benefits = retirement_pay + survivor_pay * surviving_spouse
        subtractable = min_(military_benefits, p.amount)

        eligible = person("is_tax_unit_head_or_spouse", period)
        if p.availability:
            eligible = eligible & (person("age", period) >= p.age_threshold)
        return subtractable * eligible
