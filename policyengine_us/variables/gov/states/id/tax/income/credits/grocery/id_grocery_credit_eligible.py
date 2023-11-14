from policyengine_us.model_api import *


class id_grocery_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Idaho grocery credit"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_ii
        snap_ineligible = add(spm_unit, period, ["snap"]) > 0
        incarcerated = person("is_incarcerated", period)

        return snap_ineligible & ~incarcerated
