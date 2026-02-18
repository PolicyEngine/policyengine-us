from policyengine_us.model_api import *


class is_snap_abawd_hr1_in_effect(Variable):
    value_type = bool
    entity = Person
    label = "HR1 ABAWD work requirement changes are in effect for this person"
    definition_period = MONTH
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-93.pdf",
    )

    def formula(person, period, parameters):
        # States that delay HR1 adoption have their own hr1_in_effect
        # parameter with a later effective date. Add new states here.
        federal = parameters(
            period
        ).gov.usda.snap.work_requirements.abawd.in_effect
        state_code = person.household("state_code", period)
        ca = parameters(
            period
        ).gov.states.ca.cdss.snap.work_requirements.abawd.hr1_in_effect
        return select(
            [state_code == StateCode.CA],
            [ca],
            default=federal,
        )
