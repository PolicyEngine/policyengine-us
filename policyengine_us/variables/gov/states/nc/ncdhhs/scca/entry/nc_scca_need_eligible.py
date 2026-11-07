from policyengine_us.model_api import *


class nc_scca_need_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets the North Carolina Subsidized Child Care Assistance need for care"
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = (
        # 10A NCAC 10 .0905: employment, training, and recipients unable to work
        # or train and incapable of providing care.
        "http://reports.oah.state.nc.us/ncac/title%2010a%20-%20health%20and%20human%20services/chapter%2010%20-%20subsidized%20child%20care/10a%20ncac%2010%20.0905.pdf",
        # Policy Manual Chapter 5, section II: the five need categories.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=2",
        # Section III.A: both parents or responsible adults must have a need.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=4",
        # Section III.B.5: Work First.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=8",
        # Section III.C: education.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=9",
        # Section III.D: developmental needs of the child.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=12",
        # Section III.E: Child Protective Services.
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=14",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca.need
        person = spm_unit.members
        year = period.this_year
        # Section III.B sets no minimum hours for employment, and a self-employed
        # person short of minimum wage gets fewer authorized hours under III.B.4,
        # still with a need for care. Any positive earnings count.
        employed = np.any(
            [person(source, year) > 0 for source in p.earned_income_sources],
            axis=0,
        )
        # .0905(f) covers high school, basic education and post-secondary or skills
        # training. The model can't see the 20-month limit or graduate study.
        student = person("is_full_time_student", year)
        # .0905(b) pays for recipients unable to work or train and incapable of
        # providing care, including a recipient with no other adult at home.
        # Disability stands in for the agency's determination.
        unable_to_provide_care = person("is_disabled", year) | person(
            "is_incapable_of_self_care", year
        )
        has_need = employed | student | unable_to_provide_care
        # Sections III and III.A require a need of both parents or responsible
        # adults in the household. Under section III, another adult in the home
        # blocks care only when willing and able to provide it, which the model
        # can't see, so the filers who claim an eligible child stand in for the
        # responsible adults. An incarcerated adult isn't in the household.
        eligible_child = person("nc_scca_child_eligible", period)
        claims_eligible_child = person.tax_unit.sum(eligible_child) > 0
        responsible_adult = (
            person("is_tax_unit_head_or_spouse", year)
            & claims_eligible_child
            & ~person("is_incarcerated", period)
        )
        adults_have_need = spm_unit.sum(responsible_adult & ~has_need) == 0
        # Section III.B.5 serves Work First participants through their approved
        # employment and training plan. Enrollment stands in for that plan.
        work_first = spm_unit("is_tanf_enrolled", period)
        # Section III.D serves a child whose development is delayed or at risk of
        # delay, and section III.E a child receiving Child Protective Services.
        # Disability stands in for the documented delay.
        child_need = person("is_disabled", year) | person(
            "receives_or_needs_protective_services", year
        )
        has_child_need = spm_unit.any(eligible_child & child_need)
        # This input covers job search under .0905(d), absences under .0905(c) and
        # (e), part-time study, an elderly recipient under .0905(b)(6), for which
        # the rule sets no age, and Child Welfare Services under section III.F.
        other_need = spm_unit("meets_ccdf_activity_test", year)
        return adults_have_need | work_first | has_child_need | other_need
