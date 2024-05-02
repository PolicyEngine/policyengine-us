from policyengine_us.model_api import *


class snap_gross_income_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP gross income to FPL ratio"
    documentation = (
        "SNAP gross income as a percentage of the federal poverty line"
    )
    unit = "/1"

    def formula(spm_unit, period):
        income = spm_unit("snap_gross_income", period)
        fpg = spm_unit("snap_fpg", period)
        return income / fpg
