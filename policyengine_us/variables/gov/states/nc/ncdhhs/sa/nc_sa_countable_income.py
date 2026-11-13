from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class nc_sa_countable_income(Variable):
    value_type = float
    entity = Person
    label = "North Carolina SA countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NC
    # PDF pages 185-196, 204
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=185"

    def formula(person, period, parameters):
        # SA is always a one-person budget: no spousal or parental deeming.
        # SA-3210 IV prints the $20, $65 and one-half exclusions as SA's own
        # rules; they match SSI's, so the SSI exclusion helper applies them.
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = max_(person("ssi_unearned_income", period), 0)
        other_income = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
            )
            / MONTHS_IN_YEAR
        )
        federal = person("ssi", period)
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        facility = (setting == settings.ADULT_CARE_HOME) | (
            setting == settings.SPECIAL_CARE_UNIT
        )
        # Ongoing facility budgets assume the appropriate full federal rate
        # while SSA restores a prior institutional or household reduction.
        # SSA couple computations remain an express exception to this rule
        # (SA-3210 V.D.1.e). A one-third-reduced SSI may be budgeted for at
        # most two months after admission (SA-3210 V.B.1.b); those first two
        # months are not modeled, so every facility month is an ongoing month.
        # The joint-claim test follows the marital unit: spouses who no longer
        # live together belong in separate marital units (see
        # nc_sa_care_setting), which also gives each the individual SSI amount.
        individual_claim = ~person("ssi_claim_is_joint", period.this_year)
        individual_fbr = parameters(period).gov.ssa.ssi.amount.individual
        federal = where(
            facility & individual_claim,
            max_(federal, max_(individual_fbr - other_income, 0)),
            federal,
        )
        return other_income + federal
