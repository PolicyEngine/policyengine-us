from openfisca_us.model_api import *


class snap_net_income_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "SNAP net income to FPL ratio"
    documentation = (
        "SNAP net income as a percentage of the federal poverty line"
    )
    unit = "/1"

    def formula(spm_unit, period):
        income = spm_unit("snap_net_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        return income / fpg
