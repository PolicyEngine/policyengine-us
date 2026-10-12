from policyengine_us.model_api import *


class meets_lifetime_learning_credit_identification_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets Lifetime Learning Credit identification requirements"
    documentation = "Whether the person has the taxpayer identification required for the Lifetime Learning Credit. For tax years beginning after 2025, the required identification is a Social Security number as defined in section 24(h)(7)."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/25A#g_1",
        "https://www.law.cornell.edu/uscode/text/26/24#h_7",
    ]

    def formula(person, period, parameters):
        llc = parameters(period).gov.irs.credits.education.lifetime_learning_credit
        if not llc.eligibility.requires_qualifying_ssn:
            return person("has_tin", period)

        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        return citizen | non_citizen_valid_ead
