from policyengine_us.model_api import *


class nc_scca_total_market_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program total market rate."
    reference = "https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("nc_scca_market_rate", period))
