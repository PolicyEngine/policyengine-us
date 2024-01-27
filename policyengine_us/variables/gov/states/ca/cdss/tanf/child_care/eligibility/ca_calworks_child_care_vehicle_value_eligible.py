from policyengine_us.model_api import *


class ca_calworks_child_care_vehicle_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible child for the California CalWORKs Child Care based on the vehicle value"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://dpss.lacounty.gov/en/cash/calworks.html"

    def formula(spm_unit, period, parameters):
        vehicle_value = add(spm_unit, period, ["household_vehicles_value"])
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.child_care.eligibility.resource_limit
        return vehicle_value <= p.vehicle
