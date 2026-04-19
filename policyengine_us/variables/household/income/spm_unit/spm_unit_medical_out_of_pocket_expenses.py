from policyengine_us.model_api import *


class spm_unit_medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit medical out-of-pocket expenses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Total medical out-of-pocket expenses at the SPM unit level, "
        "combining person-level imputed `medical_out_of_pocket_expenses` "
        "with rules-based premium variables (CHIP premium, Medicare Part B "
        "with IRMAA). The imputed Medicare Part B (`medicare_part_b_premiums`) "
        "that ships with person-level MOOP is subtracted out and replaced "
        "with the rules-based `income_adjusted_part_b_premium`, so reforms "
        "to the Medicare Part B base premium or IRMAA thresholds propagate "
        "through SPM resources. Consumers reading person-level "
        "`medical_out_of_pocket_expenses` directly (SNAP excess medical "
        "deduction, state itemized medical deductions) are unaffected."
    )

    def formula(spm_unit, period, parameters):
        imputed_moop = add(spm_unit, period, ["medical_out_of_pocket_expenses"])
        imputed_part_b = add(spm_unit, period, ["medicare_part_b_premiums"])
        computed_part_b = add(spm_unit, period, ["income_adjusted_part_b_premium"])
        chip_premium = add(spm_unit, period, ["chip_premium"])
        return imputed_moop - imputed_part_b + computed_part_b + chip_premium
