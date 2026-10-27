from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


class social_security_disability(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security disability benefits (SSDI)"
    unit = USD
    documentation = "Selected source with applicable benefit levers; an explicit public input is a final override."

    def formula(person, period, parameters):
        base = person("social_security_disability_base", period)
        reported = (
            person("social_security_disability_source", period)
            == SocialSecurityBenefitSource.reported
        )
        reported_factor = (
            person("social_security_disability_joint_cola_factor", period)
            * person("social_security_disability_pia_ratio_factor", period)
            * person("social_security_across_the_board_factor", period)
            * person("social_security_disability_payable_factor", period)
        )
        # The calculator applies the complete payment policy before its
        # earnings test. Its public route must not repeat any of those factors.
        return base * where(reported, reported_factor, 1)
