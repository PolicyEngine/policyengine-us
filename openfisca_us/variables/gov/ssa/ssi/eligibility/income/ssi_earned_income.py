from openfisca_us.model_api import *


class ssi_earned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        personal = person("ssi_personal_earned_income", period)
        from_ineligible_spouse = person("ssi_earned_income_deemed_from_ineligible_spouse", period)
        total_spouse_income = person("ssi_income_deemed_from_ineligible_spouse", period)
        return personal + from_ineligible_spouse * (total_spouse_income > 0)