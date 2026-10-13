from policyengine_us.model_api import *


class va_ag_allowable_income_exclusions(Variable):
    value_type = float
    entity = Person
    label = "Virginia Auxiliary Grant allowable state income exclusions"
    definition_period = MONTH
    unit = USD
    # PDF pages 127-132, 369-379, 383
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=127"
    documentation = """
    Total verified Virginia exclusions after applying Chapter D section 6 or
    Chapter H: entry-month community expenses, the applicable spouse/child
    allocation, and court-authorized guardianship fees. Enter only the allowed
    amount, not total expenses. These adjustments are additional to federal
    SSI exclusions. A percentage guardianship fee that includes the grant is
    calculated using the grant before that fee, as in Chapter D section 6.4.1.2.2.
    """
