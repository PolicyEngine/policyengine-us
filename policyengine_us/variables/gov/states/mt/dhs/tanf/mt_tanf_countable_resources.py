from policyengine_us.model_api import *


class mt_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable resources"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.401"
    defined_for = StateCode.MT
