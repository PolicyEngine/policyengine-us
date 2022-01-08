from openfisca_us.model_api import *


class spm_unit_school_meal_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Countable income for school meals"
    documentation = "SPM unit's countable income for school meal program"

    def formula(spm_unit, period, parameters):
        return spm_unit.sum(spm_unit.members("market_income", period))
