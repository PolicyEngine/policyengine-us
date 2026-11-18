from policyengine_us.model_api import *


class va_ag_certified(Variable):
    value_type = bool
    entity = Person
    label = "Certified for Virginia Auxiliary Grant care"
    definition_period = MONTH
    default_value = False
    reference = (
        "https://law.lis.virginia.gov/admincode/title22/agency30/chapter80/section10/",
        # PDF pages 69, 83-95
        "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=69",
    )
    documentation = """An approved assisted living, adult foster care or supportive housing placement with the required needs assessment. Includes the Virginia residency period or exception, pursuit of other benefits, and satisfaction of applicable transfer, public-institution and nonfinancial conditions. These are adult settings, so certification also covers the program's adult requirement. Marital units cannot change within a simulation. For months after spouses stop living in the same household, such as months after the entry month of a resident whose spouse stays at home, put them in separate marital units so that SSI and the Auxiliary Grant treat each spouse as an individual. Simulate the month of entry, including the initial month both spouses enter care together, with one marital unit."""
