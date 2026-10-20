from policyengine_us.model_api import *


class mn_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    documentation = (
        "Minnesota other additions to federal adjusted gross income reported on "
        "Schedule M1M, entered as a positive amount, excluding additions PolicyEngine "
        "calculates separately."
    )
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1m-22.pdf#page=3"
    )
