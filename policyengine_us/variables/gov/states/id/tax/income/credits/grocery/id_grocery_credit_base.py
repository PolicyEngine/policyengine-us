from policyengine_us.model_api import *


class id_grocery_credit_base(Variable):
    value_type = float
    entity = Person
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.grocery.amount

        # Count head and spouse
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_head_and_spouse = person.tax_unit.sum(head_or_spouse)
        base_credit = p.base

        return total_head_and_spouse * base_credit
