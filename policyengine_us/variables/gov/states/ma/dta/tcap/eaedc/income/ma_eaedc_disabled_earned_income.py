from policyengine_us.model_api import *


class ma_eaedc_disabled_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC disabled earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        disabled = person("is_disabled", period)
        return disabled * person("ma_eaedc_earned_income", period)
