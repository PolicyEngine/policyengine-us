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
        # Compute subtractable disability income for head and spouse separately.
        disability_income = person("disability_benefits", period)
        # Subtraction phases in and then out dollar for dollar with respect to disability income, at a given threshold.
        subtractable_disability_income = where(
            disability_income < p.threshold,
            disability_income,
            p.threshold,
        )
        is_head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        # Sum subtractable disability income for heads and spouses.
        return tax_unit.sum(subtractable_disability_income * is_head_or_spouse)
