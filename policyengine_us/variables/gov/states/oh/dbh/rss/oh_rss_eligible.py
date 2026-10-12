from policyengine_us.model_api import *


class oh_rss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Ohio RSS categorical and placement requirements"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        return (
            person("oh_rss_certified", period)
            & (person("age", period.this_year) >= p.minimum_age)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & person("medicaid_enrolled_for_ssi_state_supplement", period.this_year)
        )
