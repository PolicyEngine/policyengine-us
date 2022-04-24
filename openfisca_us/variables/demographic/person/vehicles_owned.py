from numpy import maximum
from openfisca_us.model_api import *
from random import randint, seed
from openfisca_core.populations import Population


class vehicles_owned(Variable):
    value_type = float
    entity = Person
    label = "Vehicles owned"
    unit = USD
    documentation = "Number of vehicles owned by this person"
    definition_period = YEAR

    def formula(person, period, parameters):
        # We randomly split the household's vehicles between its adults
        household = person.household
        household_vehicles = household("household_vehicles_owned", period)
        is_adult = person("is_adult", period)
        num_adults_in_household = household.sum(is_adult)
        max_vehicles = household_vehicles.max()
        adult_rank = where(is_adult, household.members_position, 100)
        vehicles = is_adult * 0
        seed(0)
        for _ in range(int(max_vehicles)):
            # Pick a random adult in each household
            selected_adult = (
                randint(0, adult_rank[is_adult].max())
                % num_adults_in_household
            )
            maximum_reached = household.sum(vehicles) >= household_vehicles
            should_add_vehicle = ~maximum_reached & (
                adult_rank == selected_adult
            )
            vehicles += where(should_add_vehicle, 1, 0)
        return vehicles
