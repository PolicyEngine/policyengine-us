from openfisca_us.model_api import *


class medicaid_income_threshold(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Medicaid FPL threshold"
    documentation = "Maximum income as a percentage of the federal poverty line to qualify for Medicaid"
    unit = "percent"

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        person_type = person("medicaid_person_type", period)
        income_threshold = parameters(period).hhs.medicaid.income_limit
        return income_threshold[state_code][person_type]
