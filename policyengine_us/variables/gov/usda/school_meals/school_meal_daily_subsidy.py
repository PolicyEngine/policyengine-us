from policyengine_us.model_api import *


def school_meal_daily_rate(spm_unit, period, parameters, *, net=False, tier=None):
    """Average each school child's meal rates, optionally net of paid rates."""
    state_group = spm_unit.household("state_group_str", period)
    child_state_group = spm_unit.project(state_group)
    in_school = spm_unit.members("is_in_k12_school", period)
    children = spm_unit.sum(in_school)
    p_amount = parameters(period).gov.usda.school_meals.amount
    result = 0
    for meal, program in (("breakfast", "sbp"), ("lunch", "nslp")):
        rates = p_amount[program]
        common_tier = spm_unit(f"school_meal_{meal}_tier", period).decode_to_str()
        child_tier = spm_unit.members(
            f"school_meal_child_{meal}_tier", period
        ).decode_to_str()
        common_rate = rates[state_group][common_tier]
        child_rate = rates[child_state_group][child_tier]
        if net:
            common_rate = common_rate - rates[state_group]["PAID"]
            child_rate = child_rate - rates[child_state_group]["PAID"]
        if tier is not None:
            common_rate = where(common_tier == tier, common_rate, 0)
            child_rate = where(child_tier == tier, child_rate, 0)
        # Preserve the common per-child rate for units without schoolchildren;
        # their annual benefit remains zero. Inputs can still override it.
        result = result + np.divide(
            spm_unit.sum(where(in_school, child_rate, 0)),
            children,
            out=common_rate.copy(),
            where=children > 0,
        )
    return result


class school_meal_daily_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidies per child per day"
    unit = USD
    documentation = (
        "Average subsidy per K-12 child per day, using each child's breakfast "
        "and lunch tiers. Units without schoolchildren retain their common "
        "per-child rate and receive no annual school-meal value."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1773#e_1_A",
        "https://www.govinfo.gov/content/pkg/FR-2026-07-16/pdf/2026-14252.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        return school_meal_daily_rate(spm_unit, period, parameters)
