from policyengine_us.model_api import *


class spm_unit_ccdf_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SPM unit CCDF subsidy"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Sum up market rate for eligible children.
        person = spm_unit.members
        market_rate = person("ccdf_market_rate", period)
        eligible = person("is_ccdf_eligible", period)
        total_eligible_market_rate = spm_unit.sum(market_rate * eligible)
        # Calculate copay and return the difference.
        total_copay = spm_unit("spm_unit_total_ccdf_copay", period)
        return max_(total_eligible_market_rate - total_copay, 0)
