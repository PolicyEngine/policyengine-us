from policyengine_us.model_api import *


class la_general_relief_net_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Net Income under the Los Angeles County General Relief after state and federal deductions"
    definition_period = YEAR
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        gross_income = add(
            spm_unit, period, ["la_general_relief_gross_income"]
        )
        paycheck_withholdings = spm_unit(
            "spm_unit_paycheck_withholdings", period
        )
        return max_(
            gross_income - paycheck_withholdings,
            0,
        )
