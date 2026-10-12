from policyengine_us.model_api import *


class ks_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF maximum benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101",
        "https://www.dcf.ks.gov/services/ees/Documents/Reports/TANF%20State%20Plan%20FFY%202024%20-%202026.pdf#page=29",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per the Kansas TANF State Plan (FFY 2024-2026) and K.A.R. 30-4-101:
        # the combined payment standard varies by assistance unit size, county
        # group, and living arrangement. The assistance unit size excludes SSI
        # recipients (KEESM 4113); the shelter portion is reduced for shared
        # living arrangements.
        p = parameters(period).gov.states.ks.dcf.tanf
        size = spm_unit("ks_tanf_assistance_unit_size", period.this_year)
        capped_size = min_(size, p.max_family_size_in_table)
        additional_people = max_(size - p.max_family_size_in_table, 0)
        county_group = spm_unit("ks_tanf_county_group", period.this_year)
        is_shared = spm_unit.household("is_shared_living", period.this_year)
        ps = p.payment_standard
        base = where(
            is_shared,
            ps.shared[county_group][capped_size],
            ps.non_shared[county_group][capped_size],
        )
        return base + additional_people * ps.additional_person_amount
