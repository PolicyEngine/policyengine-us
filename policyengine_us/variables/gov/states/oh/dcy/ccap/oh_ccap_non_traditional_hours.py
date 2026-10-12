from policyengine_us.model_api import *


class oh_ccap_non_traditional_hours(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the child receives Ohio CCAP care during non-traditional hours"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10"
