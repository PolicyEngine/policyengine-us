from policyengine_us.model_api import *


class ca_sf_caap_max_grant(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Francisco County CAAP maximum grant"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap.amount.ga
        size = spm_unit("ca_sf_caap_budget_unit_size", period)
        # The GA grant table is keyed by family size 1-10; sizes above 10 add
        # $35/person on top of the size-10 grant (SEC. 20.7-21(a) / Div 99.3-1).
        capped_size = clip(size, 1, 10)
        extra_people = max_(size - 10, 0)
        return p.by_family_size[capped_size] + p.extra_person * extra_people
