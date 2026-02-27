from policyengine_us.model_api import *


class social_security_retirement_reported(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits (reported)"
    documentation = (
        "Reported Social Security retirement benefit amount from "
        "survey data (e.g., CPS). Used in microsimulation when "
        "the reported_social_security_retirement parameter is true."
    )
    unit = USD
    uprating = "gov.ssa.uprating"
