from policyengine_us.model_api import *


class mo_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Simplified implementation - use SPM unit cash assets as proxy
        # Full implementation would include specific MO resource definitions
        # and exclusions (first vehicle, home, household goods, etc.)
        return spm_unit("spm_unit_cash_assets", period.this_year)
