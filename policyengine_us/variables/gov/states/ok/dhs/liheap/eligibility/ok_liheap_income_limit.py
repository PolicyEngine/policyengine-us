from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ok_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP annualized income limit"
    defined_for = StateCode.OK
    reference = (
        "https://oklahoma.gov/okdhs/newsroom/2026/january/comm01062026.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income.limit
        size = spm_unit("ok_liheap_household_size", period)
        capped_size = clip(size, 1, p.max_table_size)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            capped_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                capped_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        monthly_base = guideline * p.fpg_rate / MONTHS_IN_YEAR
        monthly_increment = additional_guideline * p.fpg_rate / MONTHS_IN_YEAR
        # Ceiling the base and increment separately reconciles the published
        # FY2025-FY2027 limits and additional-person amounts in Appendix C-7.
        rounding = p.rounding_increment
        rounded_base = np.ceil(monthly_base / rounding) * rounding
        rounded_increment = np.ceil(monthly_increment / rounding) * rounding
        extra_people = max_(size - p.max_table_size, 0)
        monthly_limit = rounded_base + extra_people * rounded_increment
        return where(size > 0, monthly_limit * MONTHS_IN_YEAR, 0)
