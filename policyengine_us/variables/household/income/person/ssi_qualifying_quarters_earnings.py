from policyengine_us.model_api import *


class ssi_qualifying_quarters_earnings(Variable):
    value_type = int
    entity = Person
    label = "SSI Qualifying Quarters of Earnings"
    documentation = (
        "Number of qualifying quarters of earnings for SSI eligibility"
    )
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500502135"
    default_value = 40
