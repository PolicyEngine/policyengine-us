from policyengine_us.model_api import *


class ky_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=5"

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 4(1): a single parent must work an average of at
        # least 20 hours per week; a couple must work an average of at least 40
        # combined hours per week with the lesser-working adult averaging at least
        # 5 hours. Section 6: families enrolled in Kentucky Works (K-TAP) are
        # categorically eligible, which also breaks the CCAP <-> TANF cycle.
        # Section 5: a child receiving child protective or preventive services
        # (Protection and Permanency) is eligible without a work pathway; P&P
        # status covers a child in foster care or one receiving or needing
        # child protective or preventive services.
        # We don't model the remaining pathways individually — the
        # incapacitated-parent branch (Section 4(1)(c)), teen-parent education
        # status (Section 4(1)(e)), relative-caregiver status (Section 4(1)(d)),
        # the SNAP E&T pathway (Section 6), the education/job-training pathway
        # (Section 7), and the transitional job-search, homeless, and
        # medical-leave pathways (Section 4(2)) — set the
        # meets_ccdf_activity_test input to represent them.
        p = parameters(period).gov.states.ky.dcbs.ccap.eligibility
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        num_caretakers = spm_unit.sum(is_caretaker)
        caretaker_hours = hours * is_caretaker
        total_hours = spm_unit.sum(caretaker_hours)

        # Single-parent path: the sole caretaker meets the weekly-hours floor.
        single_parent_eligible = total_hours >= p.single_parent_activity_hours
        # Couple path: combined hours meet the floor and the lesser-working
        # caretaker meets the secondary-worker minimum.
        min_caretaker_hours = spm_unit.min(where(is_caretaker, hours, np.inf))
        couple_eligible = (total_hours >= p.couple_activity_hours) & (
            min_caretaker_hours >= p.min_secondary_worker_hours
        )
        work_eligible = where(
            num_caretakers >= 2, couple_eligible, single_parent_eligible
        )
        is_tanf = spm_unit("is_tanf_enrolled", period)
        is_protection_permanency = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return is_tanf | work_eligible | is_protection_permanency | fallback
