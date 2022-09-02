from openfisca_us.model_api import *


class retrofit_energy_savings(Variable):
    value_type = float
    entity = TaxUnit
    label = "Achieved modeled energy system savings in kilowatt hours"
    definition_period = YEAR
