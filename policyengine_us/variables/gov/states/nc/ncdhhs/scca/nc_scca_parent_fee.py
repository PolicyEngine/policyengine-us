from policyengine_us.model_api import *


class nc_scca_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program parent fee"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = "https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.scca
        parent_fee_rate = p.parent_fee_rate

        family_montly_income = spm_unit('nc_scca_countable_income', period)

        parent_fee = family_montly_income * parent_fee_rate

        # Round the number and only keep the integer part
        result = int(np.round(parent_fee))
        
        return result
