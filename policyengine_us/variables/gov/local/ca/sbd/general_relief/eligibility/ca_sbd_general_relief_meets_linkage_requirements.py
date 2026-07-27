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
        # Employable: currently unemployed, or employed fewer than 100 hours
        # a month (verification that more hours are unavailable is assumed).
        weekly_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        monthly_hours = weekly_hours * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        employed = person("employment_income", period) > 0
        hours_eligible = ~employed | (monthly_hours < p.employable.monthly_hours_limit)
        # Self-employment is considered to exceed 100 hours a month.
        self_employment_income = add(
            person,
            period,
            ["self_employment_income", "sstb_self_employment_income"],
        )
        self_employed = person("is_self_employed", period.this_year) | (
            self_employment_income > 0
        )
        # Employable applicants must be available for and actively seeking
        # work; students do not meet this criterion.
        student = person("is_full_time_student", period.this_year)
        employable = hours_eligible & ~self_employed & ~student
        adult_linked = (age >= p.age_threshold) & (incapacitated | employable)
        # Children link through a cooperating parent when under 16, or when
        # aged 16 to 18 and enrolled in and attending high school full time.
        # Passing grades are not tracked.
        in_high_school = student & person("is_in_secondary_school", period.this_year)
        child_linked = (age < p.child_linkage.age_limit) | (
            (age <= p.child_linkage.student_age_limit) & in_high_school
        )
        return adult_linked | child_linked
