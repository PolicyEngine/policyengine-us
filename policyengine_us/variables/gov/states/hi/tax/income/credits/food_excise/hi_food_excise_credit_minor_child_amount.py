from policyengine_us.model_api import *


class hi_food_excise_credit_minor_child_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minor child amount for the hawaii food excise credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax
        person = tax_unit.members
        public_support_over_half = person(
            "hi_food_excise_credit_child_receiving_public_support", period
        )
        is_child = person("is_child", period)
        minor = person("age", period) < p.minor_child.age_threshold
        eligible_minor_child = is_child & minor & public_support_over_half
        minor_children = tax_unit.sum(eligible_minor_child)

        return p.minor_child.amount * minor_children
