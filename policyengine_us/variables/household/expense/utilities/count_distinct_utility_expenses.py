from policyengine_us.model_api import *


class count_distinct_utility_expenses(Variable):
    value_type = int
    entity = SPMUnit
    label = "Number of distinct utility expenses"
    documentation = "The number of distinct utility expenses."
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        UTILITIES = [
            "heating_cooling",
            # Use pre-subsidy expenses to avoid circular references
            # since electricity subsidies depend on SNAP enrollment.
            "pre_subsidy_electricity",
            "gas",
            "phone",
            "trash",
            "water",
            "sewage",
        ]
        return sum(
            [
                spm_unit(variable + "_expense", period) > 0
                for variable in UTILITIES
            ]
        )
