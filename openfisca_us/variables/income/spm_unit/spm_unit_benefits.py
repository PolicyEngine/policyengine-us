from openfisca_us.model_api import *


class spm_unit_benefits(Variable):
    value_type = float
    entity = SPMUnit
    label = "Benefits"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        PERSON_COMPONENTS = [
            "social_security",
            "ssi",
            "wic",
            "ca_cvrp",  # California Clean Vehicle Rebate Project.
        ]
        SPMU_COMPONENTS = [
            "snap",
            "free_school_meals",
            "reduced_price_school_meals",
            "lifeline",
            "acp",
            "ebb",
            # "tanf", # Exclude until defined for California.
        ]
        person_components = aggr(spm_unit, period, PERSON_COMPONENTS)
        spmu_components = add(spm_unit, period, SPMU_COMPONENTS)
        return person_components + spmu_components
