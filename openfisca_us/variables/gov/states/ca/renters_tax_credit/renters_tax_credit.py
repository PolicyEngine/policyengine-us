from openfisca_us.model_api import *


class renters_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "Renters Tax Credit"
    unit = USD
    documentation = (
        ""
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        per_vehicle = parameters(period).gov.states.ca.per_vehicle_payment
        state = person.household("state_code", period)
        vehicles_owned = None #person("vehicles_owned", period)
        capped_vehicles = None #min_(vehicles_owned, per_vehicle.max_vehicles[state])
        return None
