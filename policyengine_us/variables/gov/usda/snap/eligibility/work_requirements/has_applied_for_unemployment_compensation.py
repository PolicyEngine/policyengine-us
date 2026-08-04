from policyengine_us.model_api import *


class has_applied_for_unemployment_compensation(Variable):
    value_type = bool
    entity = Person
    label = "Has applied for unemployment compensation"
    documentation = (
        "Whether this person has applied for unemployment compensation "
        "but has not yet begun receiving it. "
        "This is an input variable that the data layer may not yet "
        "populate; see PolicyEngine/populace#244."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_v"
