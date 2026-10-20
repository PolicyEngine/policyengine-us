from policyengine_us.model_api import *


class il_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    documentation = (
        "Illinois additions to federal adjusted gross income reported on "
        "Schedule M, Lines 1-11 (total on line 12), entered as a positive amount. "
        "PolicyEngine models none of these additions separately."
    )
    reference = "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-schedule-m.pdf#page=1"
