from policyengine_us.model_api import *


class nh_ccap_disability_supplement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "New Hampshire Child Care Scholarship Program weekly disability supplement"
    definition_period = MONTH
    defined_for = "nh_ccap_eligible_child"
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.17"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.payment
        is_disabled = person("is_disabled", period.this_year)
        service_level = person("nh_ccap_service_level", period)
        supplement = p.disability_supplement.amount[service_level]
        return is_disabled * supplement
