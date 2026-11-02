from policyengine_us.model_api import *


class oh_rss_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "Ohio RSS days of placement in a partial first month"
    definition_period = MONTH
    defined_for = StateCode.OH
    default_value = 0
    documentation = "For a first month in which the person moves into the RSS living arrangement after the first day, the days from the move-in day through the last day of the month. Leave at 0 for a full month."
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01"

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
