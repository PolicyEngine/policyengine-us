from policyengine_us.model_api import *


class va_ag_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "Virginia Auxiliary Grant days in care in a partial entry month"
    definition_period = MONTH
    defined_for = StateCode.VA
    default_value = 0
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=522"
    documentation = "Days in care in an entry month that starts after the first, or a month of entry and discharge, counting the day of entry but not discharge. Leave at 0 for a full month; a value of at least the month's length is also a full month. A later discharge month is not prorated. Key the entry to its month (for example 2026-01: 15); a yearly entry applies to every month of the year."

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
