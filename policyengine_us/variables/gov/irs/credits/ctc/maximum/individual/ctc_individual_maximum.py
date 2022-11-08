from policyengine_us.model_api import *


class ctc_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC individual amount maximum"
    unit = USD
    documentation = (
        "The Child Tax Credit entitlement in respect of this person."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
    )

    formula = sum_of_variables(
        [
            "ctc_child_individual_maximum",
            "ctc_adult_individual_maximum",
        ]
    )
