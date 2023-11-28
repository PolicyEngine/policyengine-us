from policyengine_us.model_api import *


class id_grocery_credit_aged(Variable):
    value_type = float
    entity = Person
    label = "Idaho aged grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.grocery.amount
        # Aged head and spouse are eligible for an additional grocery credit amount
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        aged_amount = p.aged.calc(age)

        return person.tax_unit.sum(aged_amount)
