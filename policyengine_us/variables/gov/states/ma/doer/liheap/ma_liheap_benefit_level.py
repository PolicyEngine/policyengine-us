from policyengine_us.model_api import *


class ma_liheap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Benefit Level for Massachusetts LIHEAP payment"
    definition_period = YEAR
    defined_for = "ma_liheap_income_eligible"
    reference = "https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-november-2024/download"

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        fpg = spm_unit("ma_liheap_fpg", period)
        p = parameters(period).gov.states.ma.doer.liheap.benefit_level
        fpg_ratio = income / fpg
        # Determines benefit level (1-6) by applying income/FPG ratio to the brackets
        # defined in `p.benefit_level` (ratios >= 200% FPL yield level 6).
        # Execution is conditional on the SPM unit meeting `ma_liheap_income_eligible`.
        return p.calc(fpg_ratio)
