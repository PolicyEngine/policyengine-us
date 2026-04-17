from policyengine_us.model_api import *


class ssi_others_pay_all_meals(Variable):
    value_type = bool
    entity = Person
    label = "Others in the household pay for all meals for SSI purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1131",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500835200",
    )
