from policyengine_us.model_api import *


class EmployerPremiumContribution(Enum):
    NONE = "NONE"
    SOME = "SOME"
    ALL = "ALL"
    NA = "N/A"


class employer_premium_contribution(Variable):
    value_type = Enum
    entity = Person
    label = "Employer premium contribution"
    definition_period = YEAR
    possible_values = EmployerPremiumContribution
    default_value = StateLivingArrangement.FULL_COST
