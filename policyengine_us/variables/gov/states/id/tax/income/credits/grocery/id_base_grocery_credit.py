from policyengine_us.model_api import *


class id_base_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        #### Define path to grocery ####
        path_gc = parameters(
            period
        ).gov.states.id.tax.income.credits.grocery.amount

        #### Count head and spouse ####
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_head_and_spouse = tax_unit.sum(head_or_spouse)

        #### Define constant ####
        base_credit = path_gc.base  # base amount

        return total_head_and_spouse * base_credit
