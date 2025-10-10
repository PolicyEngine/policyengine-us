from policyengine_us.model_api import *


class tx_fpp_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Texas Family Planning Program age eligibility"
    definition_period = YEAR
    reference = "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply"
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.tx.fpp
        age_threshold = p.age_threshold
        return age <= age_threshold
