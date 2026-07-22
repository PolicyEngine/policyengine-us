from policyengine_us.model_api import *


class meets_tanf_non_cash_gross_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets gross income test for TANF non-cash benefit"
    documentation = "Income eligibility (gross income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE"
    definition_period = MONTH

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code_str", period)
        # All limits and incomes here expressed as % of FPG.
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

        # Use the gross-test income concept so states electing full
        # counting of certain ineligible aliens' income under the gross
        # income test (7 CFR 273.11(c)(3)(i)) apply it to this categorical
        # eligibility screen as well.
        gross_income = spm_unit("snap_gross_test_income_fpg_ratio", period)
        return gross_income <= gross_limit
