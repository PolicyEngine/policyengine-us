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
        # Re-derived here rather than reusing slcsp_age_curve_amount_person,
        # which gates on pays_aca_premium (false for Medicaid enrollees).
        age_rated_index = base_cost * person("slcsp_age_curve_multiplier", month)
        family_tier_share = person.tax_unit(
            "medicaid_slcsp_family_tier_person_share", period
        )
        # Family-tier share where it applies, else the age-rated index. Outer
        # max_ is a defensive floor against a negative parameter.
        return max_(where(family_tier_share > 0, family_tier_share, age_rated_index), 0)
