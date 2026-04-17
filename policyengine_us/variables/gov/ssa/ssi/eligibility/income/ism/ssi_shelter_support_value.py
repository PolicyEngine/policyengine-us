from policyengine_us.model_api import *


class ssi_shelter_support_value(Variable):
    value_type = float
    entity = Person
    label = "Actual annual value of shelter support received for SSI ISM purposes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
        "https://secure.ssa.gov/poms.nsf/lnx/0500835300",
    )
