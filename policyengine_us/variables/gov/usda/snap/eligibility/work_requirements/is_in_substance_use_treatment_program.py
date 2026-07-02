from policyengine_us.model_api import *


class is_in_substance_use_treatment_program(Variable):
    value_type = bool
    entity = Person
    label = "Regular participant in a drug or alcohol treatment program"
    documentation = (
        "Whether this person is a regular participant in a drug addiction "
        "or alcoholic treatment and rehabilitation program. "
        "This is an input variable that the data layer may not yet "
        "populate; see PolicyEngine/populace#244."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_vi"
