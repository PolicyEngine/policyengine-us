from policyengine_us.model_api import *


class ssi_medicaid_pays_majority_of_care(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pays more than half the cost of care for SSI purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500520011",
    )
