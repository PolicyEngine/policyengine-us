from policyengine_us.model_api import *


class claimed_as_dependent_on_another_return(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Is claimed as a dependent elsewhere"
    documentation = (
        "Whether the person is actually claimed, or expected to be claimed, "
        "as a dependent in another tax unit. Claimability, whether or not "
        "another taxpayer claims the person, is represented separately by "
        "claimable_as_dependent_on_another_return."
    )
