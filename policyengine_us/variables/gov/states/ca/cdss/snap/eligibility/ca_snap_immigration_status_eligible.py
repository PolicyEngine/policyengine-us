from policyengine_us.model_api import *


class ca_snap_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for California SNAP due to immigration status"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-92.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
    )

    def formula(person, period, parameters):
        # California delays OBBBA implementation to April 1, 2026 per ACL 25-92.
        p = parameters(period).gov.states.ca.cdss.snap.eligibility
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.eligible_immigration_statuses,
        )
