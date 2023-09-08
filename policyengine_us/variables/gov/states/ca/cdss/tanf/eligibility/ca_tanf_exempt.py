from policyengine_us.model_api import *


class ca_tanf_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Exempt Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.tanf.exempt"
