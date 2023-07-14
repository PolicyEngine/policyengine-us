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

        age = person("age", period)
        head = person("is_tax_unit_head", period)
        head_age = tax_unit.max(age * head)

        spouse = person("is_tax_unit_spouse", period)
        spouse_age = tax_unit.max(age * spouse)

        head_pass_age_threshold = head_age >= p.age_threshold
        spouse_pass_age_threshold = spouse_age >= p.age_threshold

        head_eligible = head & head_pass_age_threshold
        spouse_eligible = spouse & spouse_pass_age_threshold

        is_eligible = head_eligible | spouse_eligible
        return tax_unit.sum(subtractable_military_benefit * is_eligible)
