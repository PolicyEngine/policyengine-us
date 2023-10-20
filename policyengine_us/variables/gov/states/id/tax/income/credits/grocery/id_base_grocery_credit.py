from policyengine_us.model_api import *


class id_base_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        #### Define path to gc ####
        path_gc = parameters(period).gov.states.id.tax.income.credits.gc

        #### Count head and spouse ####
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        total_head_and_spouse = tax_unit.sum(head + spouse)

        #### Define constant ####
        base_credit = path_gc.amount  # base amount
        base_amount = total_head_and_spouse * base_credit

        return base_amount
