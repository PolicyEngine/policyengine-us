from openfisca_us.model_api import *


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Eligibility for Supplemental Security Income"
    label = "SSI eligibility"

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        countable_income = person("ssi_countable_income", period)
        countable_resources = person("ssi_countable_resources", period)
        return True
