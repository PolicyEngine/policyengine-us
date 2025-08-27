from policyengine_us.model_api import *


class takes_up_medicaid_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether a random eligible person unit does not enroll in Medicaid"
    definition_period = YEAR

    def formula(person, period, parameters):
        seed = person("medicaid_take_up_seed", period)
        takeup_rate = parameters(period).gov.hhs.medicaid.takeup_rate
        return seed < takeup_rate
