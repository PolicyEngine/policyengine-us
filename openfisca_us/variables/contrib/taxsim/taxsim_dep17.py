from policyengine_us.model_api import *


class taxsim_dep17(Variable):
    value_type = float
    entity = TaxUnit
    label = "Children under 17"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        age = tax_unit.members("age", period)
        return tax_unit.sum(age < 17)
