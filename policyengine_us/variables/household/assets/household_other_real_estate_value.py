from policyengine_us.model_api import *


class household_other_real_estate_value(Variable):
    value_type = float
    entity = Household
    label = "Other real estate value"
    documentation = "Value of non-homestead real estate held by the household."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
