from policyengine_us.model_api import *


class va_military_benefit_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia military benefit subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.military_benefit
        subtractable = min_(person("military_retirement_pay", period), p.amount)
        eligible = person("is_tax_unit_head_or_spouse", period)
        if p.availability:
            eligible = eligible & (person("age", period) >= p.age_threshold)
        return subtractable * eligible
