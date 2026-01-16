from policyengine_us.model_api import *


class ever_received_calworks(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ever received CalWORKs cash aid"
    definition_period = YEAR
    defined_for = StateCode.CA
    default_value = False
    reference = "https://www.cdss.ca.gov/inforesources/calworks-child-care/program-eligibility"
