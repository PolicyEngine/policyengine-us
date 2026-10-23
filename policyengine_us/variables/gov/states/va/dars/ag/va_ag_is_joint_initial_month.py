from policyengine_us.model_api import *


class va_ag_is_joint_initial_month(Variable):
    value_type = bool
    entity = Person
    label = "Virginia Auxiliary Grant couple in the initial month"
    definition_period = MONTH
    default_value = False
    # PDF pages 34-35
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=34"
    documentation = """
    The Chapter B section 6 initial-month exception, under which the assistance
    unit contains both spouses. Set for both spouses only in the initial
    application month when both were married and lived together at the start
    of the month, entered approved care, applied, and were found eligible that
    month. Simulate that month with both spouses in one marital unit. In later
    months each spouse is a separate case.
    """

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return False
