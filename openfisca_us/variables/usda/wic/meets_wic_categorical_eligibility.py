from openfisca_us.model_api import *


class meets_wic_categorical_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Meets the program participation eligibility criteria for WIC"
    )
    label = "Meets WIC categorical (program participation) eligibility"
    reference = "https://www.law.cornell.edu/uscode/text/42/1786#d_2_A"

    def formula(spm_unit, period, parameters):
        programs = parameters(period).usda.wic.categorical_eligibility
        return np.any(
            [spm_unit(program, period) for program in programs], axis=0
        )
