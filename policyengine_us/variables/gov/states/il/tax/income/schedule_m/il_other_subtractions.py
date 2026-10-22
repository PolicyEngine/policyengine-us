from policyengine_us.model_api import *


class il_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    documentation = (
        "Illinois subtractions from federal adjusted gross income reported on "
        "Schedule M not otherwise modeled, entered as a positive amount. "
        "Do not include line 13 (Bright Start, Bright Directions and College Illinois contributions), "
        "line 22 (U.S. obligations interest), or non-Illinois state and local income tax refunds "
        "on line 25, which PolicyEngine subtracts through salt_refund_income."
    )
    reference = "https://tax.illinois.gov/content/dam/soi/en/web/tax/forms/incometax/documents/currentyear/individual/il-1040-schedule-m-instr.pdf#page=2"
