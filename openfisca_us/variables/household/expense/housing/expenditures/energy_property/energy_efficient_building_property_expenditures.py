from openfisca_us.model_api import *


class energy_efficient_building_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Energy efficient building property expenditures"
    documentation = "Expenditures on energy-efficient property, including electric heat pump water heaters, electric heat pumps, central air conditioners, and natural gas, propane, or oil water heaters."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#d_3"
