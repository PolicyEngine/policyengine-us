from policyengine_us.model_api import *
from policyengine_us.tools.social_security_benefit_levers import SocialSecurityFund


class social_security_dependents_fund(Variable):
    value_type = Enum
    possible_values = SocialSecurityFund
    default_value = SocialSecurityFund.unspecified
    entity = Person
    definition_period = YEAR
    label = "Underlying Social Security dependent benefit trust fund"
    documentation = "OASI-only cuts require a supplied OASI or DI basis for a positive dependent benefit. Mixed streams require a supplied blended scenario rather than an invented allocation."
