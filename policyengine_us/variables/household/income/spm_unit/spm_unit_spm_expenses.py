from policyengine_us.model_api import *


class spm_unit_spm_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's SPM expenses (other than taxes)"
    definition_period = YEAR
    unit = USD

    adds = [
        "child_support_expense",
        "medical_out_of_pocket_expenses",
        "spm_unit_capped_work_childcare_expenses",
    ]
