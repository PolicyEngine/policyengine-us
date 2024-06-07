from policyengine_us.model_api import *


class ca_tanf_vehicle_value_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible child for the California CalWORKs based on the vehicle value"
    )
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects/CalWORKs/CalWORKs/42-215_Determining_Value_of_Property_Vehicles/42-215_Determining_Value_of_Property_Vehicles.htm"

    def formula(spm_unit, period, parameters):
        vehicle_value = add(spm_unit, period, ["household_vehicles_value"])
        p = parameters(period).gov.states.ca.cdss.tanf.cash.resources.limit
        return vehicle_value <= p.vehicle
