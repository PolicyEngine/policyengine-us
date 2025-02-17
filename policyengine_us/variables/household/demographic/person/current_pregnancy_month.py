from policyengine_us.model_api import *


class current_pregnancy_month(Variable):
    value_type = int
    entity = Person
    label = "Current pregnancy month"
    definition_period = YEAR
    defined_for = "is_pregnant"

    def formula(person, period, parameters):
        age = person("age", period)
        unborn_age = person.tax_unit.min(age * (age < 0))
        normalized_age = (unborn_age + 0.75) / 0.75
        return min_(9, np.floor(normalized_age * 9) + 1)
