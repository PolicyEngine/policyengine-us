from policyengine_us.model_api import *


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=17"

    def formula_2024(spm_unit, period, parameters):
        work_expenses = spm_unit("spm_unit_work_expenses", period)
        pre_subsidy_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        # The SPM subtracts what parents paid for child care, and child care
        # is not among its noncash benefits, so a subsidy lowers this expense
        # rather than adding to resources. childcare_expenses holds that
        # out-of-pocket amount, but it allocates expenses to children, so a
        # unit with no child nets its own expenses here.
        # Datasets fill the pre-subsidy input from the ASEC's reported spending,
        # so on microdata this nets a modeled subsidy from a reported payment.
        subsidies = spm_unit("child_care_subsidies", period)
        has_child = add(spm_unit, period, ["is_child"]) > 0
        out_of_pocket_expenses = where(
            has_child,
            spm_unit("childcare_expenses", period),
            max_(pre_subsidy_expenses - subsidies, 0),
        )
        earned_cap = spm_unit("spm_unit_head_spouse_earned_cap", period)
        return min_(work_expenses + out_of_pocket_expenses, earned_cap)
