from policyengine_us.model_api import *


class taxsim_gssi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Gross Social Security Income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["social_security"])
