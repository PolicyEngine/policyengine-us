from policyengine_us.model_api import *


class va_ag_facility_rate(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant approved facility monthly rate below the maximum"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.VA
    default_value = 0
    documentation = "The monthly rate approved for the resident's licensed assisted living facility when it is below the locality maximum; adult foster care homes use the maximum. Leave at 0 to use the maximum; a higher entry is capped at the maximum."
    reference = (
        "https://budget.lis.virginia.gov/item/2026/2/HB30/Chapter/1/332/",
        "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=520",
    )
