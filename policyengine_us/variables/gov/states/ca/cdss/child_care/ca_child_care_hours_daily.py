from policyengine_us.model_api import *


class ca_child_care_hours_daily(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Daily Hours"
    unit = "hours"
    definition_period = DAY
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.child_care.hours.child_care_hours_daily"
