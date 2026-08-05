from policyengine_us.model_api import *


class tanf_non_cash_gross_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "TANF non-cash gross income limit"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Monthly gross income limit for the TANF non-cash benefit "
        "conferring SNAP broad-based categorical eligibility."
    )

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period.this_year)
        limits = parameters(period).gov.hhs.tanf.non_cash.income_limit
        gross_limit = limits.gross[state]
        hheod = spm_unit("is_tanf_non_cash_hheod", period)
        gross_limit = where(hheod, limits.gross_hheod[state], gross_limit)

        ny = state == "NY"
        has_dependent_care = spm_unit("snap_dependent_care_deduction", period) > 0
        has_earned_income = spm_unit("snap_earned_income", period) > 0
        ny_gross_limit = where(
            has_dependent_care | hheod,
            limits.ny.dependent_care,
            where(
                has_earned_income,
                limits.ny.earned_income,
                limits.gross.NY,
            ),
        )
        gross_limit = where(ny, ny_gross_limit, gross_limit)

        # Dollar standards derive from the guideline vintage each state's
        # BBCE schedule selects (fpg_year_start_month) and follow the
        # rounding of the state's published chart: rounded up
        # (rounded_up_standard_states), to the nearest whole dollar
        # (whole_dollar_standard_states), or down
        # (rounded_down_standard_states).
        fpg = spm_unit("tanf_non_cash_fpg", period)
        raw_limit = gross_limit * fpg
        rounded_up = np.isin(state, limits.rounded_up_standard_states)
        whole_dollar = np.isin(state, limits.whole_dollar_standard_states)
        rounded_down = np.isin(state, limits.rounded_down_standard_states)
        return select(
            [rounded_up, whole_dollar, rounded_down],
            [
                np.ceil(raw_limit),
                np.floor(raw_limit + 0.5),
                np.floor(raw_limit),
            ],
            default=raw_limit,
        )
