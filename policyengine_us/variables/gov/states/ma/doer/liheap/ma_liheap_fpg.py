from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ma_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts LIHEAP federal poverty guideline"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://web.archive.org/web/20250720165524/https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        # Preserve the October guideline date for the preceding heating season.
        guideline_date = f"{period.start.year}-10-01"
        return fpg(n, state_group, guideline_date, parameters, year_lag=1)
