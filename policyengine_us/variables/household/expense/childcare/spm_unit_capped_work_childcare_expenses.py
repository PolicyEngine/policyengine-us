from policyengine_us.model_api import *


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = USD
    documentation = (
        "Over a dataset, the child care part keeps the reported amount under "
        "baseline policy and moves by the change in subsidy under a reform, "
        "which it reads from the reform's baseline arm. Core builds that arm "
        "only for a reform passed as reform=, and apply_reform builds none. A "
        "simulation built with reform= keeps its arm, under baseline policy, "
        "through any reform applied later. A reformed system passed as "
        "tax_benefit_system=, or apply_reform on a simulation built without "
        "reform=, leaves no arm, so the expense keeps the reported amount."
    )
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=17"

    def formula_2024(spm_unit, period, parameters):
        work_expenses = spm_unit("spm_unit_work_expenses", period)
        pre_subsidy_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        # The SPM subtracts what parents paid for child care, and child care
        # is not among its noncash benefits, so a subsidy lowers this expense
        # rather than adding to resources.
        simulation = spm_unit.simulation
        if simulation.is_over_dataset:
            # Datasets fill the pre-subsidy input from the ASEC, which asks
            # parents how much they spent on child care, and this rule reads
            # that as what they paid after any subsidy. Baseline policy keeps
            # that amount, and a reform moves it by the change in subsidy. A
            # baseline arm has no baseline of its own, so it keeps the amount.
            out_of_pocket_expenses = pre_subsidy_expenses
            if simulation.baseline is not None:
                baseline_spm_unit = simulation.baseline.populations["spm_unit"]
                subsidy_change = spm_unit(
                    "child_care_subsidies", period
                ) - baseline_spm_unit("child_care_subsidies", period)
                out_of_pocket_expenses = max_(pre_subsidy_expenses - subsidy_change, 0)
        else:
            # childcare_expenses holds the out-of-pocket amount, but it
            # allocates expenses to children, so a unit with no child nets its
            # own expenses here.
            subsidies = spm_unit("child_care_subsidies", period)
            has_child = add(spm_unit, period, ["is_child"]) > 0
            out_of_pocket_expenses = where(
                has_child,
                spm_unit("childcare_expenses", period),
                max_(pre_subsidy_expenses - subsidies, 0),
            )
        earned_cap = spm_unit("spm_unit_head_spouse_earned_cap", period)
        return min_(work_expenses + out_of_pocket_expenses, earned_cap)
