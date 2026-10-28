from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


class social_security_retirement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement benefits"
    unit = USD
    documentation = "Selected source with applicable benefit levers; an explicit public input is a final override."

    def formula(person, period, parameters):
        return (
            person("social_security_retirement_base", period)
            * where(
                person("social_security_retirement_source", period)
                == SocialSecurityBenefitSource.reported,
                person("social_security_retirement_joint_cola_factor", period)
                * person("social_security_retirement_pia_ratio_factor", period),
                1,
            )
            * person("social_security_across_the_board_factor", period)
            * person("social_security_retirement_payable_factor", period)
        )
