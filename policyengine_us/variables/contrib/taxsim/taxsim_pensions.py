from policyengine_us.model_api import *


class taxsim_pensions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pensions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):  # pragma: no cover
        # TAXSIM compatibility variable
        return add(tax_unit, period, ["pension_income"])
