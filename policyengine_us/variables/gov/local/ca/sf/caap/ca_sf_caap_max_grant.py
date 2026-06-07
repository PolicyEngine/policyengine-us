from policyengine_us.model_api import *


class ca_sf_caap_max_grant(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Francisco County CAAP maximum grant"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap.amount
        size = spm_unit("ca_sf_caap_budget_unit_size", period)
        # Grant tables are keyed by family size 1-10; each person beyond 10 adds
        # $35 on top of the size-10 grant (SEC. 20.7-21(e)).
        capped_size = clip(size, 1, 10)
        extra_people = max_(size - 10, 0)
        # PAES (Personalized Assisted Employment Services) recipients receive a
        # higher grant than the base General Assistance table (SEC. 20.7-21(b)
        # vs (a)). PAES enrollment is captured by the shared is_in_work_program
        # input. CALM and SSIP also use higher tiers but are not modeled at the
        # moment.
        in_paes = add(spm_unit, period, ["is_in_work_program"]) > 0
        base = where(
            in_paes,
            p.paes.by_family_size[capped_size],
            p.ga.by_family_size[capped_size],
        )
        return base + p.extra_person * extra_people
