from policyengine_us.model_api import *


class childcare_attending_days_per_month(Variable):
    value_type = int
    entity = Person
    label = "Childcare attending days per month"
    definition_period = YEAR
    unit = "days"
