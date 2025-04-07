from policyengine_us.model_api import *


class social_security(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security benefits, not including SSI"
    label = "Social Security"
    unit = USD
    adds = [
        "social_security_" + i
        for i in ["dependents", "disability", "retirement", "survivors"]
    ]
    uprating = "calibration.gov.irs.soi.social_security"
