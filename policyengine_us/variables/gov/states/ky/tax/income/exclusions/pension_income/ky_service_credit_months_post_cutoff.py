from policyengine_us.model_api import *


class ky_service_credit_months_post_cutoff(Variable):
    value_type = float
    entity = Person
    label = "Kentucky service credit months after 1997"
    definition_period = YEAR
    defined_for = StateCode.KY
