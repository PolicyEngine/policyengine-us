from policyengine_us.model_api import *


class is_hip_eligible_adult(Variable):
    value_type = bool
    entity = Person
    label = "Indiana HIP-eligible adult"
    definition_period = YEAR
    documentation = (
        "Adult enrolled in Indiana's Healthy Indiana Plan Medicaid expansion "
        "(aged 19 through 64). POWER Account contributions apply only to "
        "these members."
    )
    defined_for = StateCode.IN

    def formula(person, period, parameters):
        age = person("age", period)
        return (age >= 19) & (age < 65)
