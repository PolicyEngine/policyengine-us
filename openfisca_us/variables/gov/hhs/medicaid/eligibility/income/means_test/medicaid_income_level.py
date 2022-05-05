from openfisca_us.model_api import *


class medicaid_income_level(Variable):
    value_type = float
    entity = SPMUnit
    label = "Medicaid income level"
    unit = "/1"
    documentation = (
        "Income for Medicaid as a percentage of the federal poverty line."
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        income = spm_unit("medicaid_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        return income / fpg
