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

        # The standard is the state's percentage of the poverty guideline
        # vintage its BBCE schedule selects (fpg_year_start_month). The
        # rounding each state applies when publishing its chart is a
        # feature of that chart, not of the regulation: categorically
        # eligible households are exempt from the 7 CFR 273.9 income
        # standards, so the rounding 273.9(a)(3) prescribes for the
        # federal tests does not reach this limit. Return the exact
        # computation rather than assert an unlegislated convention.
        # Charts round in state-specific directions: Washington and
        # Maine publish figures equal to the exact value, while states
        # that round up publish a figure up to about $2 above it, so a
        # household between the two can score ineligible here slightly
        # before the published chart would say so.
        fpg = spm_unit("tanf_non_cash_fpg", period)
        return gross_limit * fpg
