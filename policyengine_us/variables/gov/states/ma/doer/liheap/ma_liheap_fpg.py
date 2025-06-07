from policyengine_us.model_api import *


class ma_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP federal poverty guideline"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download"

    def formula(spm_unit, period, parameters):
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        instant_str = f"{year - 1}-10-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        return p1 + pn * (n - 1)
