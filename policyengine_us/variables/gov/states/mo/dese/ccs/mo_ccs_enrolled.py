from policyengine_us.model_api import *


class mo_ccs_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Currently enrolled in Missouri Child Care Subsidy"
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060"
