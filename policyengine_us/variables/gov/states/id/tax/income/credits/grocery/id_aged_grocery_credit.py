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
        p = parameters(period).gov.states.id.tax.income.credits.gc

        #### Get ages for both the head and spouse ####
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        # Create boolean variables head_aged and spouse_aged to identify if they're over a certain threshold
        head_aged = p.aged_amount.calc(age_head)
        spouse_aged = p.aged_amount.calc(age_spouse)  # age threshold
        return head_aged + spouse_aged
