from policyengine_us.model_api import *


class id_grocery_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Idaho grocery credit"
    definition_period = MONTH
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        # Incarcerated people are not eligible for the grocery credit
        spm_unit = person.spm_unit
        snap_received = spm_unit("snap", period) > 0
        return ~person("is_incarcerated", period) & ~snap_received
