from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class co_leap_income_contribution_rate(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Colorado LEAP household income contribution rate"
    defined_for = StateCode.CO
    reference = "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=4,5,93"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap
        size = spm_unit("co_leap_household_size", period)
        capped_size = min_(size, p.income.additional_person_threshold)
        extra = max_(size - p.income.additional_person_threshold, 0)
        state_group = spm_unit.household("state_group_str", period)
        monthly_fpg = (
            fpg(
                capped_size,
                state_group,
                period,
                parameters,
                year_lag=p.payment.fpg_year_lag,
            )
            / MONTHS_IN_YEAR
        )
        # Inferred rounding order reproduces every published FY2026 boundary:
        # half-up monthly FPG first, then half-up each percentage of that value.
        rounded_fpg = np.floor(monthly_fpg + 0.5)
        monthly_income = spm_unit("co_leap_countable_income", period) / MONTHS_IN_YEAR
        contribution = p.payment.contribution
        conditions = [
            monthly_income <= np.floor(rounded_fpg * rate + 0.5) + extra * increment
            for rate, increment in zip(
                contribution.fpg_rates, contribution.additional_person_amounts
            )
        ]
        return select(
            conditions,
            contribution.rates[:-1],
            default=contribution.rates[-1],
        )
