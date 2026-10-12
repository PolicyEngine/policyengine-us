from policyengine_us.model_api import *


class ca_sf_caap_income_in_kind(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Francisco County CAAP in-kind income value"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap.income_in_kind
        size = spm_unit("ca_sf_caap_budget_unit_size", period)
        # The Title 22 Section 50511 in-kind chart only prints values for
        # family sizes 1 and 2. For sizes 3-10 there is no published value, so
        # we apply the size-2 value (the largest charted amount) as a
        # defensible fallback. For sizes above 10, food and clothing add
        # $35/person on top of the size-2 value; housing and utilities have no
        # published extra-person increment and stay at the size-2 value.
        charted_size = clip(size, 1, 2)
        max_size = parameters(period).gov.local.ca.sf.caap.amount.max_family_size
        extra_people = max_(size - max_size, 0)
        extra_per_person = p.extra_person * extra_people

        housing = where(
            spm_unit("ca_sf_caap_housing_provided_in_kind", period),
            p.housing[charted_size],
            0,
        )
        utilities = where(
            spm_unit("ca_sf_caap_utilities_provided_in_kind", period),
            p.utilities[charted_size],
            0,
        )
        food = where(
            spm_unit("ca_sf_caap_food_provided_in_kind", period),
            p.food[charted_size] + extra_per_person,
            0,
        )
        clothing = where(
            spm_unit("ca_sf_caap_clothing_provided_in_kind", period),
            p.clothing[charted_size] + extra_per_person,
            0,
        )
        return housing + utilities + food + clothing
