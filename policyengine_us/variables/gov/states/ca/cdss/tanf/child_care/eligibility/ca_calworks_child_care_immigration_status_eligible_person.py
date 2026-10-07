from policyengine_us.model_api import *


class ca_calworks_child_care_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California CalWORKs Child Care immigration status Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/overview.html"

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period.this_year)
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.eligibility.immigration_status

        immigration_status_str = immigration_status.decode_to_str()

        return np.isin(
            immigration_status_str,
            p.eligible_statuses,
        )
