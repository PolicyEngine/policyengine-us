from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
)


class ia_ssa_ihhrc_amount(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA in-home health-related care amount before non-income eligibility"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = (
        # 441 IAC 177.8(2) (IAC 8/5/26)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=4",
        # 441 IAC 177.10(2) (IAC 2/5/25); PDF pages 4-5
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=4",
        # PDF pages 41-42
        "https://hhs.iowa.gov/media/3987/download?inline=#page=41",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        category = person("ia_ssa_category", period)
        home = category == category.possible_values.IN_HOME_CARE
        cost = max_(person("ia_ssa_ihhrc_monthly_cost", period), 0)
        # Care costing more than the monthly ceiling is ineligible, not capped.
        approved = home & (cost <= p.ihhrc_cost_limit)
        partial = person("ia_ssa_care_partial_month_days", period)
        days = where(partial > 0, min_(partial, period.days), period.days)
        covered_cost = cost * days / period.days * approved
        # A couple's approved costs share one participation; others are alone.
        total_cost = where(
            person("ia_ssa_has_spouse", period),
            _ssi_couple_total(person, period.this_year, covered_cost),
            covered_cost,
        )
        payable = max_(total_cost - person("ia_ssa_ihhrc_participation", period), 0)
        # Allocate a common household contribution proportionately to the
        # approved costs, preserving the household's total payable benefit.
        share = np.divide(
            covered_cost,
            total_cost,
            out=np.zeros_like(covered_cost),
            where=total_cost > 0,
        )
        return payable * share
