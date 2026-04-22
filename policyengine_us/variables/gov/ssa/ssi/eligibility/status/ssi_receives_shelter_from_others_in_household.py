from policyengine_us.model_api import *


class ssi_receives_shelter_from_others_in_household(Variable):
    value_type = bool
    entity = Person
    label = "Receives shelter from others in the household for SSI purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1131",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500835200",
    )
