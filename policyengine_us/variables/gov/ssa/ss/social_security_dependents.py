from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import (
    SocialSecurityBenefitSource,
)


class social_security_dependents(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security dependents benefits"
    unit = USD
    documentation = "Selected source with applicable benefit levers; an explicit public input is a final override."

    def formula(person, period, parameters):
        base = person("social_security_dependents_base", period)
        reported = (
            person("social_security_dependents_source", period)
            == SocialSecurityBenefitSource.reported
        )
        reported_benefit = (
            base
            * where(
                reported,
                person("social_security_dependents_joint_cola_factor", period)
                * person("social_security_dependents_pia_ratio_factor", period),
                1,
            )
            * person("social_security_across_the_board_factor", period)
            * person("social_security_dependents_payable_factor", period)
        )
        # The calculator applies the complete payment policy before its
        # earnings test. Its public route must not repeat any of those factors.
        return where(reported, reported_benefit, base)
