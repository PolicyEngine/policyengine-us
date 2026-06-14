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
        # Grant tables are keyed by family size 1 to the max charted size; each
        # person beyond it adds $35 on top of the largest charted grant
        # (SEC. 20.7-21(e)).
        max_size = p.max_family_size
        capped_size = clip(size, 1, max_size)
        extra_people = max_(size - max_size, 0)
        # PAES (Personalized Assisted Employment Services) recipients receive a
        # higher grant than the base General Assistance table (SEC. 20.7-21(b)
        # vs (a)). Only count work-program participation among CAAP-eligible
        # members, so an ineligible member (SSI/CAPI/immigration, already dropped
        # from the budget unit) who is in a work program does not push the unit
        # onto the PAES table. CALM and SSIP higher tiers are not modeled.
        member = spm_unit.members
        in_paes_member = member("is_in_work_program", period) & member(
            "ca_sf_caap_eligible_person", period
        )
        in_paes = spm_unit.any(in_paes_member)
        base = where(
            in_paes,
            p.paes.by_family_size[capped_size],
            p.ga.by_family_size[capped_size],
        )
        return base + p.extra_person * extra_people
