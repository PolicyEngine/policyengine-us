from policyengine_us.model_api import *


class weekly(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Weekly Hours"
    unit = "hours"
    definition_period = WEEK
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.child_care.child_care_hours_weekly"