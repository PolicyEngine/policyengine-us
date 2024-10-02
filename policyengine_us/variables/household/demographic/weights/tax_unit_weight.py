from policyengine_us.model_api import *


class tax_unit_weight(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit weight"
    definition_period = YEAR
    uprating = "calibration.gov.census.populations.total"

    def formula(tax_unit, period, parameters):
        return tax_unit.household("household_weight", period)
