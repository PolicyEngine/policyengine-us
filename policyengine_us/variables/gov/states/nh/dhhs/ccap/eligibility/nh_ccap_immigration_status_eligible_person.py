from policyengine_us.model_api import *


class nh_ccap_immigration_status_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for New Hampshire Child Care Scholarship Program based on immigration status"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.09"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(
            immigration_status_str,
            p.eligibility.qualified_immigration_statuses,
        )
