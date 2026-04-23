from policyengine_us.model_api import *


class sc_ssi_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "South Carolina SSI State Supplement eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/south-carolina/R-126-920",
        "https://www.scdhhs.gov/communications/social-security-and-supplemental-security-income-cost-living-adjustment-increases-0",
    )
    defined_for = StateCode.SC

    def formula(person, period, parameters):
        # Per S.C. Code Regs. 126-920: aged/blind/disabled + CRCF + income < NIL
        is_aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        in_facility = person("is_in_residential_care_facility", period)
        p = parameters(period).gov.states.sc.scdhhs.ssi_state_supplement
        nil = p.net_income_limit * MONTHS_IN_YEAR
        countable_income = person("ssi_countable_income", period)
        ssi = person("ssi", period)
        income_eligible = (countable_income + ssi) < nil
        return is_aged_blind_disabled & in_facility & income_eligible
