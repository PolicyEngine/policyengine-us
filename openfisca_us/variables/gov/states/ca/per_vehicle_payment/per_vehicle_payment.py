from openfisca_us.model_api import *


class per_vehicle_payment(Variable):
    value_type = float
    entity = Person
    label = "Per-vehicle payment"
    unit = USD
    documentation = (
        "Payment to vehicle owners in respect of each owned vehicle."
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        per_vehicle = parameters(period).gov.states.ca.per_vehicle_payment
        state = person.household("state_code", period)
        vehicles_owned = person("vehicles_owned", period)
        capped_vehicles = min_(vehicles_owned, per_vehicle.max_vehicles[state])
        return capped_vehicles * per_vehicle.amount[state]
