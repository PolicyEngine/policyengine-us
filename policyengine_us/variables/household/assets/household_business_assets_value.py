from policyengine_us.model_api import *


class household_business_assets_value(Variable):
    value_type = float
    entity = Household
    label = "Business asset value"
    documentation = "Value of business assets held by the household."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
