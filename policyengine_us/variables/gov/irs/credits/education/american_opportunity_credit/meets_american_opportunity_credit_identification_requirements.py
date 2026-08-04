from policyengine_us.model_api import *


class meets_american_opportunity_credit_identification_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets American Opportunity Credit identification requirements"
    documentation = "Whether the person has the taxpayer identification required for the American Opportunity Credit. For tax years beginning after 2025, the required identification is a Social Security number as defined in section 24(h)(7)."
    definition_period = YEAR
    reference = [
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A",
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section24",
    ]

    def formula(person, period, parameters):
        aoc = parameters(period).gov.irs.credits.education.american_opportunity_credit
        if not aoc.eligibility.requires_qualifying_ssn:
            return person("has_tin", period)

        ssn_card_type = person("ssn_card_type", period)
        ssn_card_types = ssn_card_type.possible_values
        citizen = ssn_card_type == ssn_card_types.CITIZEN
        non_citizen_valid_ead = ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
        return citizen | non_citizen_valid_ead
