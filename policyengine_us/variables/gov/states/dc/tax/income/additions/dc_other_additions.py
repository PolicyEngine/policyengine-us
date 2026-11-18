from policyengine_us.model_api import *


class dc_other_additions(Variable):
    value_type = float
    entity = Person
    label = "DC other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    documentation = (
        "District of Columbia other additions to federal adjusted gross income "
        "reported on Form D-40, Schedule I, Calculation A, Line 7 (Other additions), "
        "entered as a positive amount."
    )
    reference = "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2024_D40_Booklet_011525.pdf#page=55"
