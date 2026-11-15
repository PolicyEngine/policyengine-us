from policyengine_us.model_api import *


class mt_ccap_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Enrolled in the Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.202"
    # Distinguishes a continuing recipient at annual redetermination, who faces
    # the graduated limit, from a first-time applicant (the default), who faces
    # the initial limit; gov.states.mt.dphhs.ccap.income.fpg_limit holds both.
