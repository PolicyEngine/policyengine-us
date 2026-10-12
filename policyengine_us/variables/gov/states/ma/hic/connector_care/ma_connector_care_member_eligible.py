from policyengine_us.model_api import *


class ma_connector_care_member_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Member eligible for Massachusetts ConnectorCare"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=5",
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=6",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=1",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=2",
    )
    documentation = (
        "A person counts as a ConnectorCare enrollee when they are eligible "
        "for the federal ACA premium tax credit. ConnectorCare requires "
        "federal APTC eligibility (956 CMR 12.04(3)(a)2 to 12.04(2) to 45 CFR "
        "155.305(f)), so this single gate embeds citizenship and lawful "
        "presence, on-Marketplace enrollment, the married-filing-separately "
        "exclusion, the required-contribution income test, and the absence of "
        "Medicare or MassHealth minimum essential coverage, all via the "
        "federal chain. "
        "This count of APTC-eligible members is the per-person enrollee "
        "premium multiplier for the household subsidy (CO/WA convention)."
    )

    def formula(person, period, parameters):
        return person("is_aca_ptc_eligible", period)
