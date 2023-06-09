from policyengine_us.model_api import *


class va_federal_state_employees_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia federal state employees subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.va.tax.income.subtractions.disability_income

        employment_income = person("employment_income", period)
        state_or_federal_salary = person("state_or_federal_salary", period)
        subtractable_federal_state_salary = where(
            employment_income > p.amount, 0, state_or_federal_salary
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = head | spouse
        return tax_unit.sum(
            subtractable_federal_state_salary * is_head_or_spouse
        )
