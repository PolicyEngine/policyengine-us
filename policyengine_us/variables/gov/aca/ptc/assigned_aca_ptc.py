from policyengine_us.model_api import *


class assigned_aca_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Assigned ACA premium tax credit for tax unit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/36B"

    def formula(tax_unit, period, parameters):
        return tax_unit("aca_ptc", period) * tax_unit(
            "takes_up_aca_if_eligible", period
        )
