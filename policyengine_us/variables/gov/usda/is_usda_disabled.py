from policyengine_us.model_api import *


class is_usda_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = (
        "Meets the benefit-receipt half of the SNAP 'elderly or disabled "
        "member' definition (7 CFR 271.2), which counts any SSI receipt, "
        "whether based on age, blindness, or disability."
    )
    label = "USDA disabled status"

    def formula(person, period, parameters):
        programs = parameters(period).gov.usda.disabled_programs
        return np.logical_or.reduce([person(program, period) for program in programs])
