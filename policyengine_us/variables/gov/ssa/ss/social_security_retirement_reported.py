from policyengine_us.model_api import *


class social_security_retirement_reported(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits"
    unit = USD
    uprating = "calibration.gov.irs.soi.social_security"
