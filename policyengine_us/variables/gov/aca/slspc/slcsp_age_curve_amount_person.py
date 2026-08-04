from policyengine_us.model_api import *


class slcsp_age_curve_amount_person(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost, for people in age curve states"
    unit = USD
    definition_period = MONTH
    defined_for = "pays_aca_premium"

    def formula(person, period, parameters):
        base_cost = person.household("slcsp_age_0", period)
        multiplier = person("slcsp_age_curve_multiplier", period)
        age_curve_applies = person.tax_unit("slcsp_age_curve_applies", period)
        return base_cost * multiplier * age_curve_applies
