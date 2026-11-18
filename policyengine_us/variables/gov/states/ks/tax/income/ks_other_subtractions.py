from policyengine_us.model_api import *


class ks_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KS
    documentation = (
        "Kansas other subtractions from federal adjusted gross income reported on "
        "Schedule S, Part A, Line A25 (Other subtractions from federal adjusted gross income), "
        "entered as a positive amount."
    )
    reference = "https://www.ksrevenue.gov/pdf/ip25.pdf#page=13"
