from policyengine_us.model_api import *


class oh_ccap_has_special_accommodations(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the Ohio CCAP child has approved special accommodations"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-09"
