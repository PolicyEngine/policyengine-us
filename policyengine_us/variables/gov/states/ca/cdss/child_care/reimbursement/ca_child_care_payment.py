from policyengine_us.model_api import *


class ca_child_care_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Child Care final payment"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        payment_standard = person("ca_child_care_payment_standard", period)
        time_coefficient = person("ca_child_care_time_coefficient", period)
        payment_factor = person("ca_child_care_payment_factor", period)

        return spm_unit.sum(
            payment_standard * time_coefficient * payment_factor
        )
