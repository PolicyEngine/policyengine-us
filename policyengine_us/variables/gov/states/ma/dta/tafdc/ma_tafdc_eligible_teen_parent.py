from policyengine_us.model_api import *


class ma_tafdc_eligible_teen_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is an eligible teen parent for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        is_parent = person("is_parent", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tafdc.eligibility.age_threshold
        age = person("age", period)
        return is_parent & (age < p.teen_parent)
