from policyengine_us.model_api import *


class person_receives_aca(Variable):
    value_type = bool
    entity = Person
    label = "Person receives ACA"
    documentation = (
        "Whether a person is eligible for ACA premium tax credits and is in a "
        "tax unit that takes up ACA coverage."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        return person.tax_unit("takes_up_aca_if_eligible", period) & person(
            "is_aca_ptc_eligible", period
        )
