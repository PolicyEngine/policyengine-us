from policyengine_us.model_api import *


class snap_child_support_gross_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction from gross income"
    unit = USD
    documentation = (
        "Deduction for child support payments when computing SNAP gross income"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    def formula(spm_unit, period, parameters):
        child_support = add(spm_unit, period, ["child_support_expense"])
        # Exclude ineligible members' share per SNAP proration rules (result always >= 0 since prorate_fraction < spm_unit_size)
        prorate_fraction = spm_unit("snap_prorate_fraction", period.this_year)
        spm_unit_size = spm_unit("spm_unit_size", period)
        child_support_after_proration = child_support * (
            1 - prorate_fraction / spm_unit_size
        )
        state = spm_unit.household("state_code_str", period)
        p = parameters(period).gov.usda.snap.income.deductions
        return p.child_support[state] * child_support_after_proration
