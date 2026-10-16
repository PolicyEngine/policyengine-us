from policyengine_us.model_api import *


class hi_food_excise_credit_minor_child_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minor child's number for the Hawaii Food/Excise Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n311_i.pdf#page=1",
        "https://files.hawaii.gov/tax/forms/2025/n311_i.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax
        person = tax_unit.members
        public_support_over_half = person(
            "hi_food_excise_credit_child_receiving_public_support", period
        )
        is_child = person("is_child", period)
        minor = person("age", period) < p.minor_child.age_threshold
        # Form N-311 line 3 lists minor children who, among other tests,
        # "Cannot be claimed as a dependent by another taxpayer"; the filers
        # are listed on line 2.
        claimable_elsewhere = person("claimable_as_dependent_on_another_return", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        eligible_minor_child = (
            is_child & minor & public_support_over_half & ~claimable_elsewhere & ~filer
        )

        return tax_unit.sum(eligible_minor_child)
