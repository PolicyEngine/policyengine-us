from policyengine_us.model_api import *


class mn_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN
    documentation = (
        "Minnesota other subtractions from federal adjusted gross income reported on "
        "Schedule M1M, entered as a positive amount, excluding subtractions PolicyEngine "
        "calculates separately."
    )
    reference = "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1m-22.pdf"
