from openfisca_us.model_api import *


class capped_residential_energy_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped residential energy property expenditures"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#b_3"

    formula = sum_of_variables(
        [
            "capped_advanced_main_air_circulating_fan_expenditures",
            "capped_energy_efficient_building_property_expenditures",
            "capped_qualified_furnace_or_hot_water_boiler_expenditures",
        ]
    )
