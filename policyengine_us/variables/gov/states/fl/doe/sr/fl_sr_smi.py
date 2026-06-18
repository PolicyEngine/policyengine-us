from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class fl_sr_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida School Readiness monthly state median income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://www.elclc.org/wp-content/uploads/2025/10/2025-2026-Sliding-Fee-Schedule-for-10012025-4-and-6-Percent.pdf#page=2",
        "https://flrules.elaws.us/fac/6m-4.200",
    )

    def formula(spm_unit, period, parameters):
        # The October 2025 sliding fee schedule uses the federal fiscal year 2026
        # state median income estimates. Pin the SMI to the federal fiscal year
        # (which starts October 1) rather than the simulation period, mirroring the
        # New Jersey CCAP pattern.
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, instant_str, parameters)
        return annual_smi / MONTHS_IN_YEAR
