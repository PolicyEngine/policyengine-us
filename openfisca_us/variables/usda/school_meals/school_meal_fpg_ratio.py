from openfisca_us.model_api import *


class school_meal_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's federal poverty ratio for school meal program"
    unit = "/1"

    def formula(spm_unit, period, parameters):
        income = spm_unit("school_meal_countable_income", period)
        return income / spm_unit("spm_unit_fpg", period)
