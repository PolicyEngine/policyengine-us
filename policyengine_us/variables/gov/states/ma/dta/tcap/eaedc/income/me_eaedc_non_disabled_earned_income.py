from policyengine_us.model_api import *


class ma_eaedc_non_disabled_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income of a non disabled person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        disabled = person("is_disabled", period)
        return ~disabled * person("ma_eaedc_total_earned_income", period)
        # rename this to ma_eaedc_non_disabled_dependent_earned_income 
        # def formula(person, period, parameters):
        #      return add(spm_unit, period, ["ma_eaedc_total_earned_income" - "eaedc_disabled_dependent_earned_income"]
            