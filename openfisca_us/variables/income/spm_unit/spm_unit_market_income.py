from openfisca_us.model_api import *


class spm_unit_market_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Market income"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return aggr(spm_unit, period, ["market_income"])
