from policyengine_us.model_api import *


class wa_birth_to_three_eceap_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age-eligible for Washington Birth to Three ECEAP"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.578",
        "https://www.startearly.org/app/uploads/2021/06/Final-Summary-of-Fair-Start-for-Kids-Act.pdf#page=9",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.wa.dcyf.eceap.birth_to_three_eceap
        return age < p.age_limit
