from policyengine_us.model_api import *


class ca_calworks_child_care_days_per_month(Variable):
    value_type = int
    entity = Person
    label = "California CalWORKs Child Care days per month"
    definition_period = MONTH
    defined_for = StateCode.CA
