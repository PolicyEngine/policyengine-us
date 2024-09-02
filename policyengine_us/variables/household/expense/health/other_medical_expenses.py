from policyengine_us.model_api import *


class other_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Other medical expenses"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
