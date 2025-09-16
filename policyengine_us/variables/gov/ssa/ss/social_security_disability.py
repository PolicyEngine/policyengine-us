from policyengine_us.model_api import *


class social_security_disability(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Social Security disability benefits (SSDI)"
    unit = USD
    uprating = "gov.ssa.uprating"
    reference = "https://www.ssa.gov/benefits/disability/"

    adds = ["ssdi_individual_benefit"]
