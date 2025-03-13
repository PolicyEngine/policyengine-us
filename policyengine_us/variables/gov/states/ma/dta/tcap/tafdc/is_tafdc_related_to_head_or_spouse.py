from policyengine_us.model_api import *


class is_tafdc_related_to_head_or_spouse(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is related to the head or spouse under the TAFDC regulations"
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-310"
    )
    default_value = True
