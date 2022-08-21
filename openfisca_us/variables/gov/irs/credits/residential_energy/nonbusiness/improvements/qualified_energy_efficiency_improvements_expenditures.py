from openfisca_us.model_api import *


class qualified_energy_efficiency_improvements_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Expenditures on qualified energy efficiency improvements"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#c"

    formula = sum_of_variables(
        [
            "energy_efficient_door_expenditures",
            "energy_efficient_insulation_expenditures",
            "energy_efficient_roof_expenditures",
            "energy_efficient_window_expenditures",
        ]
    )
