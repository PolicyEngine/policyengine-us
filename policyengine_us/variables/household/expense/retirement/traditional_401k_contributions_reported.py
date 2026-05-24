from policyengine_us.model_api import *


class traditional_401k_contributions_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported traditional 401(k) contributions"
    unit = USD
    documentation = "Contributions reported to traditional 401(k) accounts before statutory contribution limits."
    definition_period = YEAR
