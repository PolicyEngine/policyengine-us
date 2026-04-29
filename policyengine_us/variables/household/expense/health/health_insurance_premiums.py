from policyengine_us.model_api import *


class health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Person-level health insurance premiums used by statutory medical "
        "expense definitions. SPM MOOP uses its own decomposed premium stack."
    )

    adds = [
        "health_insurance_premiums_without_medicare_part_b",
        "medicare_part_b_premium",
    ]
