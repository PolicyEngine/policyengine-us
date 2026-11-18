from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


class social_security_disability_source(Variable):
    value_type = Enum
    possible_values = SocialSecurityBenefitSource
    default_value = SocialSecurityBenefitSource.reported
    entity = Person
    definition_period = YEAR
    label = "Social Security disability benefit source"
