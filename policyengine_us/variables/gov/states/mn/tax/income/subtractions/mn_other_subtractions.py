from policyengine_us.model_api import *


class mn_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    documentation = (
        "Minnesota subtractions from federal adjusted gross income reported on "
        "Schedule M1M, Line 40 (Total subtractions), entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf"
