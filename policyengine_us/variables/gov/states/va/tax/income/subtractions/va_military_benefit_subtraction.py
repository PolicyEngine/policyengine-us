from policyengine_us.model_api import *


class va_military_benefit_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia military benefit subtraction"
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
        ).gov.states.va.tax.income.subtractions.military_benefit

        subtractable_military_benefit = min_(
            person("military_retirement_pay", period), p.amount
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        if p.availability:
            age = person("age", period)
            age_eligible = age >= p.age_threshold
            head_or_spouse_eligible = head_or_spouse & age_eligible
        else:
            head_or_spouse_eligible = head_or_spouse
        return tax_unit.sum(
            subtractable_military_benefit * head_or_spouse_eligible
        )
