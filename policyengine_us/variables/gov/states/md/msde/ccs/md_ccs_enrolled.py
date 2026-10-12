from policyengine_us.model_api import *


class md_ccs_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Maryland Child Care Scholarship (CCS)"
    defined_for = StateCode.MD
