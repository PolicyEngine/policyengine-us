from policyengine_us.model_api import *


class meets_school_meal_categorical_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "School meal categorical eligibility"
    documentation = "Whether this SPM unit is eligible for free school meal via participation in other programs"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/245.2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.school_meals
        programs = add(spm_unit, period, p.categorical_eligibility)
        return np.any(programs)
