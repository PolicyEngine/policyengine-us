from openfisca_us.model_api import *


class taxsim_scorp(Variable):
    value_type = float
    entity = TaxUnit
    label = "S-corp income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["partnership_s_corp_income"])
