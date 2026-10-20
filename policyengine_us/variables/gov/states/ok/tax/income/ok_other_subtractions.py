from policyengine_us.model_api import *


class ok_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    documentation = (
        "Oklahoma other subtractions from federal adjusted gross income reported on "
        "Schedule 511-A (Other subtractions), entered as a positive amount, excluding "
        "subtractions PolicyEngine calculates separately."
    )
    reference = "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=16"
