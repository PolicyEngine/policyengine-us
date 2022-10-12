from policyengine_us.model_api import *


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("market_income", period))
