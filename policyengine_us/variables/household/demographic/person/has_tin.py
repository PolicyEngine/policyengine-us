from policyengine_us.model_api import *


class has_tin(Variable):
    value_type = bool
    entity = Person
    label = "Has TIN (ITIN or SSN)"
    definition_period = YEAR
    default_value = True

    def formula(person, period, parameters):
        simulation = person.simulation

        # Canonical path: allow direct `has_tin` inputs to override the formula.
        holder = simulation.get_holder("has_tin")
        if period in holder.get_known_periods():
            array = holder.get_array(period)
            if array is not None:
                return array

        # Temporary migration path: honor legacy `has_itin` inputs until callers move.
        legacy_holder = simulation.get_holder("has_itin")
        if period in legacy_holder.get_known_periods():
            array = legacy_holder.get_array(period)
            if array is not None:
                return array

        return np.full(person.count, True)
