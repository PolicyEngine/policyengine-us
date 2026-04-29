from policyengine_us.model_api import *


class medical_expense_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums for medical expense definitions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Person-level health insurance premiums counted by statutory medical "
        "expense definitions. Uses a direct premium input when supplied; "
        "otherwise combines reported non-Medicare premiums with modeled "
        "Medicare Part B premiums."
    )

    def formula(person, period, parameters):
        direct = person("health_insurance_premiums", period)
        non_medicare = person(
            "health_insurance_premiums_without_medicare_part_b", period
        )
        medicare_enrolled = person("medicare_enrolled", period)
        medicare_part_b = person("medicare_part_b_premium", period) * medicare_enrolled
        decomposed = non_medicare + medicare_part_b
        return where(direct != 0, direct, decomposed)
