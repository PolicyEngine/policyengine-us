from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ca_child_care_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care State Median Income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://www.cde.ca.gov/sp/cd/ci/mb2505.asp"

    def formula(spm_unit, period, parameters):
        # California uses July 1 fiscal year for SMI
        year = period.start.year
        month = period.start.month
        if month >= 7:
            instant_str = f"{year}-07-01"
        else:
            instant_str = f"{year - 1}-07-01"

        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)

        return smi(size, state, instant_str, parameters) / MONTHS_IN_YEAR
