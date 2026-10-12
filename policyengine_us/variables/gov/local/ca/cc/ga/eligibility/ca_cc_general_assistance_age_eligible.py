from policyengine_us.model_api import *


class ca_cc_general_assistance_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Eligible for Contra Costa County General Assistance based on age requirements"
    )
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.cc.general_assistance
        age = person("monthly_age", period)
        return age >= p.age_threshold
