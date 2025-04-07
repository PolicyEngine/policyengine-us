from policyengine_us.model_api import *

class or_liheap_hhs_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "State Median income for LIHEAP"
    unit = USD
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        year = period.start.year
        month = period.start.month

        # LIHEAP uses October values from the current year if month >= March
        # Otherwise, it uses October values from the previous year
        if month >= 3:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"

        return spm_unit("gov/hhs/hhs_smi", instant_str)


