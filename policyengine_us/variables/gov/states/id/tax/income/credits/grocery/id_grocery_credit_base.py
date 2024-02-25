from policyengine_us.model_api import *


class id_grocery_credit_base(Variable):
    value_type = float
    entity = Person
    label = "Idaho base grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        base = parameters(
            period
        ).gov.states.id.tax.income.credits.grocery.amount.base
        eligibility_fraction = person(
            "id_grocery_credit_prorated_eligiblity_fraction", period
        )
        return base * eligibility_fraction
