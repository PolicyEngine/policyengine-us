from policyengine_us.model_api import *


class household_rental_property_debt(Variable):
    value_type = float
    entity = Household
    label = "Rental property debt"
    documentation = "Debt secured by household rental property assets."
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
