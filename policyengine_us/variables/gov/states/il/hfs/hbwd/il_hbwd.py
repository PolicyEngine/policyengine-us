from policyengine_us.model_api import *


class il_hbwd(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Health Benefits for Workers with Disabilities"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/hbwd.html",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/about.html",
    )
    defined_for = StateCode.IL

    adds = ["il_hbwd_person"]
