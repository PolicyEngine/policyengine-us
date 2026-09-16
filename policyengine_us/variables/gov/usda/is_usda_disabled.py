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
    reference = "https://www.law.cornell.edu/cfr/text/7/271.2"

    def formula(person, period, parameters):
        programs = parameters(period).gov.usda.disabled_programs
        # Each entry is truthiness-tested: boolean flags count when true,
        # and amount entries (ssi, social_security_disability) count when
        # positive over the period.
        received = [add(person, period, [program]) > 0 for program in programs]
        return np.logical_or.reduce(received)
