from policyengine_us.model_api import *


class hi_liheap_qualified_member(Variable):
    value_type = bool
    entity = Person
    label = "Qualified member for Hawaii LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/07/Policies-and-Procedures-2020.pdf#page=6",
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=59",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.dhs.liheap.eligibility
        # COFA citizens can be represented by an explicit qualified-status flag;
        # the shared immigration enum does not yet distinguish COFA status.
        qualified_status = person("is_citizen_or_legal_immigrant", period)
        ssn_card_type = person("ssn_card_type", period)
        has_ssn = ssn_card_type != ssn_card_type.possible_values.NONE
        ssn_required = person("age", period) >= p.ssn_min_age
        return qualified_status & (has_ssn | ~ssn_required)
