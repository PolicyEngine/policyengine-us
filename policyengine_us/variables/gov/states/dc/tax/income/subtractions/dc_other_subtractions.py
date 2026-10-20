from policyengine_us.model_api import *


class dc_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "DC other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    documentation = (
        "District of Columbia other subtractions from federal adjusted gross income "
        "reported on Form D-40, Schedule I, Calculation B, Line 13 (Other), "
        "entered as a positive amount. Do not include Social Security, unemployment compensation, "
        "disability exclusions, U.S. government interest, or state/local income tax refunds, "
        "which PolicyEngine computes separately."
    )
    reference = "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2024_D40_Booklet_011525.pdf#page=55"
