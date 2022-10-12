from policyengine_us.model_api import *


class taxsim_taxsimid(Variable):
    value_type = int
    entity = TaxUnit
    label = "Tax unit ID"
    definition_period = ETERNITY

    def formula(tax_unit, period, parameters):
        return tax_unit("tax_unit_id", period)
