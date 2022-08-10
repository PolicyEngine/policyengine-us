from openfisca_us.model_api import *


class fuel_cell_property_capacity(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capacity of purchased fuel cells"
    documentation = (
        "Kilowatts of capacity of qualified fuel cell properties purchased."
    )
    unit = "kW"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#b_1"
