from policyengine_us.model_api import *


class oh_rss_days_of_placement(Variable):
    value_type = int
    entity = Person
    label = "Days of Ohio RSS placement in the month"
    definition_period = MONTH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01"

    def formula(person, period, parameters):
        return period.days
