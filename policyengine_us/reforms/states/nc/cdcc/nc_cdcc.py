from policyengine_us.model_api import *


def create_nc_cdcc() -> Reform:
    class nc_cdcc(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina CDCC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC







    class reform(Reform):
        def apply(self):
            self.update_variable(or_income_subtractions)
            self.update_variable(or_rebate_subtraction)

    return reform


