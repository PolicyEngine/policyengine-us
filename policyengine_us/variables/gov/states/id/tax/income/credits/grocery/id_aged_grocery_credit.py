from policyengine_us.model_api import *


class id_aged_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho aged grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        #### Define path to gc ####
        path_gc = parameters(period).gov.states.id.tax.income.credits.gc

        #### Get ages for both the head and spouse ####
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        total_head_and_spouse = tax_unit.sum(head + spouse)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        # Create boolean variables head_aged and spouse_aged to identify if they're over 65
        age_threshold = path_gc.age_eligibility  # age threshold
        head_aged = age_head >= age_threshold
        spouse_aged = age_spouse >= age_threshold  # age threshold
        total_aged = head_aged + spouse_aged

        #### Define constant ####
        age_amount = path_gc.aged_amount  # additional amount
        aged_addition = age_amount * total_aged

        return aged_addition
