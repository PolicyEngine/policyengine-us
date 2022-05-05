from openfisca_us.model_api import *


class meets_medicaid_income_threshold(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets Medicaid income threshold"
    documentation = "Whether the person meets the Medicaid income threshold given their state, age, and family structure."

    def formula(person, period, parameters):
        fpg_income_threshold = person("medicaid_income_threshold", period)
        income_share_of_fpg = person.spm_unit("medicaid_income_level", period)
        return income_share_of_fpg <= fpg_income_threshold
