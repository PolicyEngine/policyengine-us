from policyengine_us.model_api import *


class ks_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KS
    documentation = (
        "Kansas other additions to federal adjusted gross income reported on "
        "Schedule S, Part A, Line A8 (Other additions to federal adjusted gross income), "
        "entered as a positive amount."
    )
    reference = "https://www.ksrevenue.gov/pdf/ip25.pdf#page=11"
