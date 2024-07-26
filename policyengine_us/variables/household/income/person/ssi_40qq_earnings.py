from policyengine_us.model_api import *

class ssi_40qq_earnings(Variable):
    value_type = bool
    entity = Person
    label = "40 Qualifying Quarters of Earnings"
    documentation = "Has necessary 40 Qualifying Quarters of Earnings for SSI"
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500502135"
