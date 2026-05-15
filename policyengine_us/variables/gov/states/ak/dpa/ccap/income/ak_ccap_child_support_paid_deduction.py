from policyengine_us.model_api import *


class ak_ccap_child_support_paid_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP child support paid deduction"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    adds = ["child_support_expense"]
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=242"
