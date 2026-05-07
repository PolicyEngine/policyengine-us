from policyengine_us.model_api import *


class sc_ssi_state_supplement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "South Carolina SSI State Supplement"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/regulations/south-carolina/R-126-910",
        "https://www.law.cornell.edu/regulations/south-carolina/R-126-920",
    )
    defined_for = "sc_ssi_state_supplement_eligible"

    def formula(person, period, parameters):
        # Per S.C. Code Regs. 126-910: OSS = max(0, NIL - countable income)
        p = parameters(period).gov.states.sc.scdhhs.ssi_state_supplement
        nil = p.net_income_limit * MONTHS_IN_YEAR
        countable_income = person("ssi_countable_income", period)
        ssi = person("ssi", period)
        return max_(0, nil - countable_income - ssi)
