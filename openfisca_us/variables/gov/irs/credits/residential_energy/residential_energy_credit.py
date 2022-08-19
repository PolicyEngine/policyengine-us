from openfisca_us.model_api import *


class residential_energy_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Residential energy credit from Form 5695"
    unit = USD

    formula = sum_of_variables(
        [
            "residential_energy_efficient_property_credit",
            "nonbusiness_energy_property_credit",
        ]
    )
