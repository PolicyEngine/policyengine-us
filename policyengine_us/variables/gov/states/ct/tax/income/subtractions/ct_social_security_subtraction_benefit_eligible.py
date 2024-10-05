from policyengine_us.model_api import *


class ct_social_security_benefit_subtraction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut social security benefit subtraction"
    definition_period = YEAR
    defined_for = StateCode.CT
