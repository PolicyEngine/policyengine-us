from openfisca_us.model_api import *


class NewElectricVehicleClassification(Enum):
    VAN = "Van"
    SUV = "Sport utility vehicle"
    PICKUP = "Pickup truck"
    OTHER = "Other"


class new_clean_vehicle_classification(Variable):
    value_type = Enum
    possible_values = NewElectricVehicleClassification
    default_value = NewElectricVehicleClassification.OTHER
    entity = TaxUnit
    label = "New clean vehicle classification"
    definition_period = YEAR
