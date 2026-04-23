from policyengine_us.model_api import *


class ssi_receives_outside_shelter_support(Variable):
    value_type = bool
    entity = Person
    label = "Receives shelter support from others for SSI ISM purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500835300",
    )
