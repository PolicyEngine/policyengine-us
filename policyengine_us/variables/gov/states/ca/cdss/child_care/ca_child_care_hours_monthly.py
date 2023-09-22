from policyengine_us.model_api import *


class ca_child_care_hours_monthly(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Monthly Hours"
    unit = "hours"
    definition_period = MONTH
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.child_care.hours.child_care_hours_monthly"
