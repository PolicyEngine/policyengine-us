from policyengine_us.model_api import *


class household_rental_property_value(Variable):
    value_type = float
    entity = Household
    label = "Rental property value"
    documentation = "Value of rental property assets held by the household."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
