from policyengine_us.model_api import *


class va_ag_certified(Variable):
    value_type = bool
    entity = Person
    label = "Certified for Virginia Auxiliary Grant care"
    definition_period = MONTH
    default_value = False
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf"
    documentation = """An approved assisted living, adult foster care or supportive housing placement with the required needs assessment. Includes the Virginia residency period or exception, pursuit of other benefits, and satisfaction of applicable transfer, public-institution and nonfinancial conditions."""
