from openfisca_us.model_api import *


class spm_unit_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "Benefits"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        BENEFITS = [
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
            # "tanf", # Exclude until defined for California.
        ]
        return add(spm_unit, period, BENEFITS)
