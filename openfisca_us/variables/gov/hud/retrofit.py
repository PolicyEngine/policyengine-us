from openfisca_us.model_api import *


class retrofit_energy_savings(Variable):
    value_type = float
    entity = Household
    label = "Achieved modeled energy system savings in Killowatt-hours"
    definition_period = YEAR
