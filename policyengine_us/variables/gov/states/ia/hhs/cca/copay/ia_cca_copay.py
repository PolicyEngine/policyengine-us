from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ia.hhs.cca.copay.ia_cca_sliding_fee_level import (
    SLIDING_FEE_LEVELS,
)
from policyengine_us.variables.gov.states.ia.hhs.cca.copay.ia_cca_exit_fee_level import (
    EXIT_FEE_LEVELS,
)


class ia_cca_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Iowa CCA family fee"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=11"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.copay
        person = spm_unit.members
        is_eligible_child = person("ia_cca_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        is_in_care_child = is_eligible_child & in_care
        children_in_care = spm_unit("ia_cca_children_in_care", period)

        # --- Mechanism A: CCA and CCA Plus sliding unit fee ---
        # A flat fee per half-day unit, assessed on only one child (the one
        # receiving the most units), with the unit-fee column set by the
        # number of children in care (one, two, or three or more).
        sliding_level = spm_unit("ia_cca_sliding_fee_level", period)
        children_col = clip(children_in_care, 1, 3).astype(int)
        unit_fee = 0
        for i, level in enumerate(SLIDING_FEE_LEVELS):
            unit_fee = unit_fee + where(
                sliding_level == i,
                p.sliding_fee.unit_fee[level][children_col],
                0,
            )
        monthly_units = person("ia_cca_monthly_units", period)
        focal_units = spm_unit.max(monthly_units * is_in_care_child)
        sliding_copay = unit_fee * focal_units

        # --- Mechanism B: CCA Exit percentage of cost of care ---
        # A percentage of the cost of care for each child in care, summed
        # across children. The fee chart picks the Basic or Special Needs
        # threshold table for each child separately, so the percentage is
        # resolved per child before summing.
        exit_level = person("ia_cca_exit_fee_level", period)
        exit_pct = 0
        for i, level in enumerate(EXIT_FEE_LEVELS):
            exit_pct = exit_pct + where(exit_level == i, p.exit.fee_pct[level], 0)
        child_expense = person("pre_subsidy_childcare_expenses", period)
        exit_copay = spm_unit.sum(exit_pct * child_expense * is_in_care_child)

        in_exit_tier = spm_unit("ia_cca_in_exit_tier", period)
        copay = where(in_exit_tier, exit_copay, sliding_copay)

        # Families eligible without regard to income pay no fee
        # (IAC 441-170.2(1)"b"; family fee chart).
        income_exception = spm_unit("ia_cca_income_exception", period)
        return where(income_exception, 0, copay)
