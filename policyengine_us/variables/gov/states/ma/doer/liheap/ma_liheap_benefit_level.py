from policyengine_us.model_api import *


class ma_liheap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Benefit Level for Massachusetts LIHEAP payment"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://web.archive.org/web/20250720165524/https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download",
        "https://www.mass.gov/info-details/energy-burden-inquiry",
    )

    def formula(spm_unit, period, parameters):
        income = spm_unit("ma_liheap_income", period)
        fpg = spm_unit("ma_liheap_fpg", period)
        p = parameters(period).gov.states.ma.doer.liheap.benefit_level
        fpg_ratio = income / fpg
        # Each chart column pays households up to and including its income
        # figure: at or below 100% of the poverty level is level 1, above 100%
        # and at or below 125% is level 2, and above 200% is level 6. The
        # thresholds are those band tops, so the lookup uses right=True.
        return p.calc(fpg_ratio, right=True)
