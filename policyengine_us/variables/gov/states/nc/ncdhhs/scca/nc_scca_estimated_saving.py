from policyengine_us.model_api import *


class nc_scca_estimated_saving(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = 'nc_scca_entry_eligible'

    # adds = ['nc_scca_market_rate']
    # subtracts = ["nc_scca_parent_fee"]

    def formula(spm_unit, period, parameters):
        total_market_rate = add(
            spm_unit,
            period,
            ["nc_scca_market_rate"],
        )
        
        # total_market_rate = spm_unit.sum(spm_unit.members("nc_scca_market_rate", period))
        parent_fee = spm_unit("nc_scca_parent_fee", period)
        return max_(total_market_rate - parent_fee, 0)
