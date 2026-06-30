from policyengine_us.model_api import *


class oh_ccap_is_accredited(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the child's Ohio CCAP provider is accredited"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10"
