from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class co_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "State median income for Colorado CCAP"
    unit = USD
    documentation = "The state median income used to determine eligibility for Colorado's Child Care Assistance Program. This differs from the HHS definition by basing it on the prior year if before October, and dividing by 12."
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        state_code = spm_unit.household("state_code_str", period.this_year)
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        return smi(size, state_code, instant_str, parameters) / MONTHS_IN_YEAR
