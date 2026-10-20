from policyengine_us.model_api import *


class wi_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Wisconsin other subtractions from federal adjusted gross income reported on "
        "Schedule SB (Other subtractions from income), entered as a positive amount, "
        "excluding subtractions PolicyEngine calculates separately."
    )
    reference = "https://www.revenue.wi.gov/TaxForms2024/2024-ScheduleSB-Inst.pdf"
