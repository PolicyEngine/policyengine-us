from openfisca_us.model_api import *


class spm_unit_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "Benefits"
    definition_period = YEAR
    unit = USD

    formula = sum_of_variables(
        [
            "social_security",
            "ssi",
            "ca_cvrp",  # California Clean Vehicle Rebate Project.
            "snap",
            "wic",
            "free_school_meals",
            "reduced_price_school_meals",
            "lifeline",
            "acp",
            "ebb",
            "basic_income",
            # "tanf", # Exclude until defined for California.
        ]
    )
