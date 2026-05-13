from policyengine_us.model_api import *


class sc_ssi_state_supplement_pna(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "South Carolina SSI State Supplement personal needs allowance"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/regulations/south-carolina/R-126-910",
        "https://www.scdhhs.gov/communications/social-security-and-supplemental-security-income-cost-living-adjustment-increases-0",
    )
    defined_for = "sc_ssi_state_supplement_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.sc.scdhhs.ssi_state_supplement.personal_needs_allowance
        # Per S.C. Code Regs. 126-910(G): SSI-only PNA if no other
        # countable income; higher PNA if other income sources exist
        ssi_only = person("ssi_countable_income", period) == 0
        return where(ssi_only, p.ssi_only, p.other_income) * MONTHS_IN_YEAR
