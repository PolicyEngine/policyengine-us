from policyengine_us.model_api import *


class il_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) assistance unit size"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60"
    defined_for = StateCode.IL

    adds = ["il_payment_eligible_child", "il_payment_eligible_parent"]
