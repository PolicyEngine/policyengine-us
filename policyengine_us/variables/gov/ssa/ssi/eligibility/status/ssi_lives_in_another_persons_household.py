from policyengine_us.model_api import *


class ssi_lives_in_another_persons_household(Variable):
    value_type = bool
    entity = Person
    label = "Lives in another person's household for SSI purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1132",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500835200",
    )
