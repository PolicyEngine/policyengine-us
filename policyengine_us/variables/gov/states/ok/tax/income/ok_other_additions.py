from policyengine_us.model_api import *


class ok_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    documentation = (
        "Oklahoma other additions to federal adjusted gross income reported on "
        "Schedule 511-B (Other additions), entered as a positive amount."
    )
    reference = "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=16"
