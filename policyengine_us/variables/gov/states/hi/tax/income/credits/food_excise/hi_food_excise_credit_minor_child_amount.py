from policyengine_us.model_api import *


class hi_food_excise_credit_minor_child_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minor child amount for the Hawaii Food/Excise Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax

        return p.minor_child.amount * tax_unit(
            "hi_food_excise_credit_minor_child_count", period
        )
