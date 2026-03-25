from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class me_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine CCAP State Median Income for family size"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=12"

    def formula(spm_unit, period, parameters):
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        return smi(size, state, instant_str, parameters) / MONTHS_IN_YEAR
