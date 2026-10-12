from policyengine_us.model_api import *


class va_ag_days_eligible(Variable):
    value_type = int
    entity = Person
    label = "Days of Virginia Auxiliary Grant care in the initial month"
    definition_period = MONTH
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf"
    documentation = """
    Use actual days in an initial partial month, including entry and excluding
    discharge. Later discharge months retain the full monthly care rate.
    """

    def formula(person, period, parameters):
        return period.days
