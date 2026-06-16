from policyengine_us.model_api import *


class ia_cca_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in Iowa CCA"
    # Whether the family is already enrolled in Iowa Child Care Assistance.
    # Iowa applies the higher ongoing income limits (CCA Plus and CCA Exit)
    # only to families enrolled at annual redetermination; new applicants
    # face the lower initial limits.
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"
