from policyengine_us.model_api import *


class il_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) assistance unit size"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.300"
    defined_for = StateCode.IL

    adds = [
        "il_tanf_payment_eligible_child",
        "il_tanf_payment_eligible_parent",
    ]
