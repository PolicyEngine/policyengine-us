from policyengine_us.model_api import *


class la_general_relief_motor_vehicle_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Los Angeles County General Relief based on the motor vehicle value requirements"
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        household = spm_unit.household
        lives_in_vehicle = household("lives_in_vehicle", period)
        vehicle_value = household("household_vehicles_value", period)
        p = parameters(
            period
        ).gov.local.ca.la.general_relief.eligibility.limit.motor_vehicle
        vehicle_value_limit = where(
            lives_in_vehicle, p.value.homeless, p.value.resident
        )
        vehicle_value_eligible = vehicle_value <= vehicle_value_limit
        vehicles_owned = household("household_vehicles_owned", period)
        return vehicle_value_eligible & (vehicles_owned <= p.cap)
