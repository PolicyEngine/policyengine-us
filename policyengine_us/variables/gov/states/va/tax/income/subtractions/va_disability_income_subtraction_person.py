from policyengine_us.model_api import *


class va_disability_income_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia disability income subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.disability_income
        subtractable = min_(person("disability_benefits", period), p.amount)
        return subtractable * person("is_tax_unit_head_or_spouse", period)
