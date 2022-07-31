from openfisca_us.model_api import *


class new_electric_vehicle_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for new electric vehicle credit"
    documentation = "Eligible for nonrefundable credit for the purchase of a new electric vehicle"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/30D"
    defined_for = "purchased_qualifying_new_electric_vehicle"

    def formula(tax_unit, period, parameters):
        return True
