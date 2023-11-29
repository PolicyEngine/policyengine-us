from policyengine_us.model_api import *


class id_grocery_credit_base(Variable):
    value_type = float
    entity = Person
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = "id_grocery_credit_eligible"

    def formula(person, period, parameters):
        return parameters(
            period
        ).gov.states.id.tax.income.credits.grocery.amount.base
