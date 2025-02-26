from policyengine_us.model_api import *


class ma_eaedc_disabled_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income of each disabled person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        return (
            disabled
            * dependent
            * person("ma_eaedc_total_earned_income", period)
        )
