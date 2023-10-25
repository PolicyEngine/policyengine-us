from policyengine_us.model_api import *


class ky_service_credit_months_pre_1998(Variable):
    value_type = float
    entity = Person
    label = "Kentucky service credit months before 1998"
    definition_period = YEAR
    defined_for = StateCode.KY
