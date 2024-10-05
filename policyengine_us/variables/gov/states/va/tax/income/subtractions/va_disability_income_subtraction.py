from policyengine_us.model_api import *


class va_disability_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia disability income subtraction"
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
        # Subtraction phases in and then out dollar for dollar with respect to disability income, at a given threshold.
        subtractable_disability_income = min_(
            person("disability_benefits", period), p.amount
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = head | spouse
        return tax_unit.sum(subtractable_disability_income * is_head_or_spouse)
