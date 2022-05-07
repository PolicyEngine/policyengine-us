from openfisca_us.model_api import *


class meets_school_meal_categorical_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "School meal categorical eligibility"
    documentation = "Whether this SPM unit is eligible for free school meal via participation in other programs"
    definition_period = YEAR
    reference = "https://www.fns.usda.gov/cn/extending-categorical-eligibility-additional-children-household"

    def formula(spm_unit, period, parameters):
        programs = parameters(period).usda.school_meals.categorical_eligibility
        return np.any(
            [spm_unit(program, period) for program in programs], axis=0
        )
