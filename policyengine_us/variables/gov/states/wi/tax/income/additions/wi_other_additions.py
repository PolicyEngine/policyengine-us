from policyengine_us.model_api import *


class wi_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WI
    documentation = (
        "Wisconsin other additions to federal adjusted gross income reported on "
        "Schedule AD (Other additions to income), entered as a positive amount, "
        "excluding additions PolicyEngine calculates separately."
    )
    reference = "https://www.revenue.wi.gov/TaxForms2024/2024-ScheduleAD-Inst.pdf"
