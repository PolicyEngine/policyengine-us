from policyengine_us.model_api import *


class medicaid_slcsp_cost_index(Variable):
    value_type = float
    entity = Person
    label = "Medicaid SLCSP cost index"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        month = period.first_month
        base_cost = person.household("slcsp_age_0", month)
        age_rated_index = base_cost * person("slcsp_age_curve_multiplier", month)
        family_tier_share = person.tax_unit(
            "medicaid_slcsp_family_tier_person_share", period
        )
        return max_(where(family_tier_share > 0, family_tier_share, age_rated_index), 0)
