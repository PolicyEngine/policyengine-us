from policyengine_us.model_api import *


class ct_social_security_benefit_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit subtraction"
    definition_period = YEAR
    defined_for = "ct_social_security_benefit_subtraction_eligible"
