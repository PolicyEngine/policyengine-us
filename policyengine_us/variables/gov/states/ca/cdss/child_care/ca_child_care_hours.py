from policyengine_us.model_api import *


class ca_child_care_hours(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Hours"
    unit = hours
    definition_period = Month
    defined_for = StateCode.CA

    adds = "gov.states.ca.cdss.tanf.income.sources.earned"
