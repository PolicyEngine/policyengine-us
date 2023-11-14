from policyengine_us.model_api import *


class hi_food_excise_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii Food/Excise Tax Credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=44"

    def formula(tax_unit, period, parameters):
        # filer can not be a dependent on another return
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        total_amount = add(
            tax_unit,
            period,
            [
                "hi_food_excise_credit_minor_child_amount",
                "hi_food_excise_exemption_amount",
            ],
        )
        return ~dependent_elsewhere * total_amount
