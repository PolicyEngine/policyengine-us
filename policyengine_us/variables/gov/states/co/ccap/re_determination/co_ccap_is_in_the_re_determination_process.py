from policyengine_us.model_api import *


class co_ccap_is_in_the_re_determination_process(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether applicants are in the re-determination process of the Colorado Child Care Assistance Program"
    definition_period = YEAR
    defined_for = StateCode.CO
