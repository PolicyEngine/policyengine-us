from policyengine_us.model_api import *


class il_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    documentation = (
        "Illinois other additions to federal adjusted gross income reported on "
        "Schedule M, Line 10 (Other additions), entered as a positive amount."
    )
    reference = "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-instr.pdf#page=7"
