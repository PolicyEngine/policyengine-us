from policyengine_us.model_api import *


class mt_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Enrolled in the Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202"
    # Distinguishes a continuing recipient (at annual redetermination, eligible
    # under the ARM 37.80.202(2) graduated 185% FPG limit) from a first-time
    # applicant (the default, held to the 150% initial limit in 37.80.202(1)).
