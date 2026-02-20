from policyengine_us.model_api import *


class is_snap_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP due to immigration status"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
        "https://www.law.cornell.edu/uscode/text/8/1612",
        "https://www.fns.usda.gov/snap/obbb-alien-eligibility",
    )

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        p = parameters(period).gov.usda.snap.eligibility
        federal_eligible = np.isin(
            immigration_status_str,
            p.eligible_immigration_statuses,
        )
        ca_eligible = person("ca_snap_immigration_status_eligible", period)

        return federal_eligible | ca_eligible
