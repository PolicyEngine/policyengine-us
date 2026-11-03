from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._medicaid_parents import (
    medicaid_parent_indices,
)


class nv_ccdp_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on Purpose of Care activity"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = (
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=76",
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=40",
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=66",
    )

    def formula(spm_unit, period, parameters):
        # MS 400 series: the applicant, every other required adult and minor
        # parents must be in an approved Purpose of Care activity. MS 216.1 lists
        # a child's parents and stepparents, a minor parent's major parents, and
        # a guardian or designated relative caregiver and their spouses, not
        # every adult at the address. parent_1_id and parent_2_id name parents,
        # whoever claims the child, and the Medicaid helper adds a lone linked
        # parent's established spouse as the stepparent. A child or minor parent
        # with no linked parent in the unit falls to the head and spouse of their
        # tax unit. So without ids a parent who doesn't claim the child isn't
        # checked, and an adult who shares the child's tax unit is, because that
        # tax unit reads its second adult as a spouse. The stepparent step takes
        # the same reading, so a second adult in a linked parent's tax unit is
        # required unless marked a dependent or linked to that parent by parent
        # ids. MS 216.1 also lists a parent's domestic partner, whom this reaches
        # only through a shared tax unit or the cohabiting spouses flag.
        #   - POC 420 (working) needs monetary compensation and sets no minimum
        #     hours, so earnings stand in for it. A self-employment loss still
        #     counts: MS 306.37 asks for an enterprise for gain.
        #   - POC 450 (student) needs six or more credit hours at an accredited
        #     college, which every full-time college student meets. We don't
        #     track credit hours, so part-time students use the input below.
        #     MS 450.1 has minor parents attend school for a diploma or GED. We
        #     don't track diplomas, so a minor parent who works also passes.
        #   - POC 470 (disability) requires someone else to care for the child
        #     outside child care hours. A disabled caretaker is covered when
        #     another caretaker works or studies. When the someone else is any
        #     other adult at home, MS 470 still applies, and the input below
        #     covers that case.
        #   - meets_ccdf_activity_test covers what we don't model individually:
        #     POC 430 (job search), POC 460 (training), and the student and
        #     disability cases above that fall outside these proxies.
        #   - is_tanf_enrolled covers POC 410 (TANF NEON referrals); using the
        #     enrollment input rather than computed TANF eligibility breaks the
        #     CCDP <-> TANF circular dependency.
        #   - is_homeless covers POC 440 (Homeless Self-Sufficiency Plan), a
        #     need-for-care reason that belongs inside the activity test.
        #   - Protective services (State Plan Section 2.2; Manual CPS/Foster
        #     Group Set, MS 410) make a child needing care eligible regardless
        #     of caretaker activity, so a child in foster care or receiving/
        #     needing protective services satisfies the need-for-care test on
        #     its own (mirrors the nv_ccdp_copay protective-care waiver).
        # We don't track activity-hour verification or overlapping two-parent
        # schedules at the moment (MS 400 series), nor the job-search 90-day or
        # student/job-search funding-availability limits. Annual earnings mark
        # a caretaker as working in every month of the year.
        person = spm_unit.members
        is_eligible_child = person("nv_ccdp_eligible_child", period)
        is_minor_parent = person("is_child", period.this_year) & person(
            "is_parent", period.this_year
        )
        needs_parent = is_eligible_child | is_minor_parent
        unit = spm_unit.members_entity_id
        is_linked_parent = np.zeros(person.count, dtype=bool)
        has_linked_parent = np.zeros(person.count, dtype=bool)
        for parent in medicaid_parent_indices(person, period.this_year):
            linked = needs_parent & (parent >= 0) & (unit[parent] == unit)
            is_linked_parent[parent[linked]] = True
            has_linked_parent[linked] = True
        is_claimant = person.tax_unit.any(needs_parent & ~has_linked_parent) & (
            person("is_tax_unit_head_or_spouse", period.this_year)
        )
        is_caretaker = is_linked_parent | is_claimant | is_minor_parent
        is_working = (person("employment_income", period.this_year) > 0) | (
            person("self_employment_income", period.this_year) != 0
        )
        is_student = person("is_full_time_college_student", period.this_year)
        in_school = is_minor_parent & person("is_in_k12_school", period.this_year)
        in_activity = is_working | is_student | in_school
        is_covered = in_activity | person("is_disabled", period.this_year)
        has_active_caretaker = spm_unit.any(is_caretaker & in_activity)
        has_uncovered_caretaker = spm_unit.any(is_caretaker & ~is_covered)
        modeled_activity = has_active_caretaker & ~has_uncovered_caretaker
        meets_activity_test = spm_unit("meets_ccdf_activity_test", period.this_year)
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        # Restrict the protective-care pathway to an nv_ccdp_eligible_child so a
        # non-eligible household member does not confer eligibility.
        in_protective_care = is_eligible_child & (
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        has_protective_child = spm_unit.any(in_protective_care)
        return (
            modeled_activity
            | meets_activity_test
            | is_tanf_enrolled
            | is_homeless
            | has_protective_child
        )
