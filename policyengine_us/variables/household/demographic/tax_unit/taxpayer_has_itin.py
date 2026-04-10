from policyengine_us.model_api import *


class taxpayer_has_itin(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head or spouse has ITIN (deprecated alias; use taxpayer_has_tin)"

    def formula(tax_unit, period, parameters):
        return tax_unit("taxpayer_has_tin", period)
