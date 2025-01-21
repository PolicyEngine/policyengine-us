from policyengine_us.model_api import *


class nc_scca_estimated_saving(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina Subsidized Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = 'nc_scca_entry_eligible'

    # # is this the correct way
    # adds = ['nc_scca_market_rate']
    # subtracts = ["nc_scca_parent_fee"]

    # or this is the correct way
    def formula(spm_unit, period, parameters):
        total_market_rate = spm_unit('nc_scca_total_market_rate', period)
        parent_fee = spm_unit('nc_scca_parent_fee', period)

        total_estimated_savings = total_market_rate - parent_fee

        return total_estimated_savings

