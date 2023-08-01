from policyengine_us.model_api import *


class pell_grant_schedule_percent(Variable):
    value_type = float
    entity = Person
    label = "Percent of Year Student is in School"
    definition_period = YEAR

    def formula(person, period):
        return 1
