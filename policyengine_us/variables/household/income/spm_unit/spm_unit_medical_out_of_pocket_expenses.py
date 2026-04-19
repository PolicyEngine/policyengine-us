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
        "with rules-based premium variables that are defined at higher "
        "entities (e.g. `chip_premium` at the tax unit level). Used by "
        "`spm_unit_spm_expenses` for SPM resource accounting. For the "
        "person-level imputed figure alone, consumers that don't need "
        "rules-based premium additions should read "
        "`medical_out_of_pocket_expenses` directly."
    )

    def formula(spm_unit, period, parameters):
        return add(
            spm_unit,
            period,
            [
                "medical_out_of_pocket_expenses",
                "chip_premium",
            ],
        )
