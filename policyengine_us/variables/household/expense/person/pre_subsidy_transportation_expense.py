from policyengine_us.model_api import *


class pre_subsidy_transportation_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    label = "Pre-subsidy transportation expense"
    unit = USD
