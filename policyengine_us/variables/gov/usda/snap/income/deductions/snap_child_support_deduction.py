from policyengine_us.model_api import *


class snap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction"
    unit = USD
    documentation = (
        "Deduction from SNAP gross income for child support payments"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    # Excluding deduction for child support, which is applies to the gross income
    # calculation
    def formula(spm_unit, period, parameters):
        child_support = add(spm_unit, period, ["child_support_expense"])
        gross_income_deduction = spm_unit(
            "snap_child_support_gross_income_deduction", period
        )
        # Per 273.11(c)(1), only eligible members' share of expenses count as deductions
        proration_factor = spm_unit("snap_deduction_proration_factor", period)
        prorated_child_support = child_support * proration_factor
        return max_(prorated_child_support - gross_income_deduction, 0)
