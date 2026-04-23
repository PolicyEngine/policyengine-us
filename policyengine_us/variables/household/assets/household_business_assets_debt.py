from policyengine_us.model_api import *


class household_business_assets_debt(Variable):
    value_type = float
    entity = Household
    label = "Business asset debt"
    documentation = "Debt secured by household business assets."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
