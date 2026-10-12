from policyengine_us.model_api import *


class ssi_qualifying_quarters_earnings(Variable):
    value_type = int
    entity = Person
    label = "SSI Qualifying Quarters of Earnings"
    documentation = (
        "Number of qualifying quarters of earnings for SSI eligibility. The "
        "same legal count (8 USC 1612(a)(2)(B) and 1645) governs the SNAP "
        "qualified alien waiting period exception, which reads the separate "
        "input snap_alien_qualifying_quarters (default 0). When both inputs "
        "are supplied for a person, they should hold the same number."
    )
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500502135"
    default_value = 40
