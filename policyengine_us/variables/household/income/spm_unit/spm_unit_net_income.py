from policyengine_us.model_api import *


class spm_unit_net_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Net income"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        market_income = spm_unit("spm_unit_market_income", period)
        benefits = spm_unit("spm_unit_benefits", period)
        taxes = spm_unit("spm_unit_taxes", period)
        return market_income + benefits - taxes
