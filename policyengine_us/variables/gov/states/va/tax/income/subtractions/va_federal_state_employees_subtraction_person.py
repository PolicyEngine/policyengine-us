from policyengine_us.model_api import *


class va_federal_state_employees_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia federal and state employees subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.disability_income
        employment_income = person("irs_employment_income", period)
        subtractable = where(
            employment_income > p.amount,
            0,
            person("state_or_federal_salary", period),
        )
        return subtractable * person("is_tax_unit_head_or_spouse", period)
