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
        
        subtractable_military_benefit = min_(person("military_benefit", period), p.amount)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)

        head_age = person("age_head", period)
        spouse_age = person("age_spouse", period)
        head_pass_age_threshold = head_age >= p.age_threshold
        spuse_pass_age_threshold = spouse_age >= p.age_threshold

        head_eligible = head & head_pass_age_threshold
        spouse_eligible = spouse & spuse_pass_age_threshold

        eligible = head_eligible | spouse_eligible
        return tax_unit.sum(subtractable_military_benefit * eligible)
