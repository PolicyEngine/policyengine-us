from policyengine_us.model_api import *


class hi_food_excise_credit_minor_child_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minor child's number for the Hawaii Food/Excise Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax

        return (
            tax_unit("hi_food_excise_credit_minor_child_amount", period)
            / p.minor_child.amount
        )
