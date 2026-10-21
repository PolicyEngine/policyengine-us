from policyengine_us.model_api import *


class sd_ssp_care_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "South Dakota SSP care residence days in a partial month"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06:09"
    documentation = "Days of long-term care residence in a month of less than a full month's residence. Leave at 0 for a full month. Enter it for the month, since a yearly value applies to every month."

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
