from policyengine_us.model_api import *


class ca_sbd_general_relief_meets_linkage_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Meets San Bernardino County General Relief linkage requirements"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/39fc00fa-7256-4849-9f07-7710402996f1.docx",
        "https://wp.sbcounty.gov/tad/wp-content/uploads/sites/25/GR-Orientation-PPT-_05.2025-master.pdf#page=8",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.eligibility
        age = person("monthly_age", period)
        # Incapacity — a verified physical or mental incapacity preventing
        # any gainful activity — is proxied with is_incapable_of_self_care.
        # Social unemployability is a caseworker-discretion category with no
        # model input, so it folds into the assumed-compliance employable
        # path.
        incapacitated = person("is_incapable_of_self_care", period.this_year)
        # The handbook's employable definition (unemployed, or employed
        # under 100 hours a month) and its self-employment bar are
        # deliberately not modeled: any worker whose income is low enough
        # to pass the income test could leave the job and qualify
        # categorically, so in steady state the income test alone governs
        # need. The 90-day voluntary-quit disqualification that would delay
        # that path has no model input and is likewise not modeled, along
        # with the WDD-registration and weekly job-search compliance
        # requirements (assumed met).
        # Employable applicants must be available for and actively seeking
        # work; students do not meet this criterion. Both the handbook and
        # the orientation deck bar students without qualification, so full-
        # and part-time students both fail the employable path (part-time
        # college is the only part-time enrollment input).
        full_time_student = person("is_full_time_student", period.this_year)
        student = full_time_student | person(
            "is_part_time_college_student", period.this_year
        )
        employable = ~student
        adult_linked = (age >= p.age_threshold) & (incapacitated | employable)
        # Children link through a cooperating parent when under 16, or when
        # aged 16 to 18 and enrolled in and attending high school full time.
        # Passing grades are not tracked, and the cooperating-parent
        # requirement is not modeled: a 16-to-18 high-school student with no
        # parent in the unit still links here (and at 18 satisfies the
        # unit's adult-age requirement alone) — an approximation, since the
        # county's child linkage runs through a parent applicant.
        in_high_school = full_time_student & person(
            "is_in_secondary_school", period.this_year
        )
        # "Aged 16 to 18" is a whole-number age band: a child is "aged 18"
        # until their 19th birthday, and age is a float.
        child_linked = (age < p.child_linkage.age_limit) | (
            (age < p.child_linkage.student_age_limit + 1) & in_high_school
        )
        return adult_linked | child_linked
