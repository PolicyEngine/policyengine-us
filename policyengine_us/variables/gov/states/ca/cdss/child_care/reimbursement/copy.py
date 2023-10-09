from policyengine_us.model_api import *


class copy(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care Payment Standard"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.child_care.rate_ceilings.standard
        #provider = spm_unit("ca_child_care_provider", period)
        #category = spm_unit("ca_child_care_time_based_category", period)

        persons = spm_unit.members
        child = persons("is_child", period)
        age = persons("age", period)
        child_payment = p["child_care_centers"]["daily"]["full_time"].calc(age) * child
  
        return spm_unit.sum(child_payment)
