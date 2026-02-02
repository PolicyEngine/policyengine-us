from policyengine_us.model_api import *


class is_snap_ineligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Is an ineligible student for SNAP"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2015#e"

    def formula(person, period, parameters):
        # Base rule: Students enrolled at least half-time in higher education
        # are ineligible (K-12 students are not affected by this rule)
        is_higher_ed_student = person("is_snap_higher_ed_student", period)

        # Eight statutory exceptions that make students eligible:

        # Exception 1: Under 18 or age 50 or older
        age = person("age", period)
        p = parameters(period).gov.usda.snap.student
        meets_age_exception = p.age_threshold.calc(age)

        # Exception 2: Not physically or mentally fit (disabled)
        meets_disability_exception = person("is_disabled", period)

        # Exception 3: Assignment through workforce/employment programs
        # (WIOA, career/technical ed, remedial/basic education)
        # Not modeled

        # Exception 4: Employed at least 20 hours per week or work-study
        meets_work_hours_exception = person(
            "meets_snap_work_exception", period
        )

        # Exception 5: Parent with responsibility for dependent child under 6,
        # or child 6-11 when adequate child care is not available
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        # (Exceptions 5 and 8 are implemented together)
        meets_parent_exception = person("meets_snap_parent_exception", period)

        # Exception 6: Receiving TANF benefits (part A of title IV)
        tanf = person("tanf_person", period)
        receives_tanf = tanf > 0

        # Exception 7: Enrolled as result of participation in work incentive
        # program under title IV (TANF work programs) or successor programs
        # Not modeled

        # Student is INELIGIBLE if they are a higher ed student AND
        # they do NOT meet ANY of the eight exceptions
        meets_any_exception = (
            meets_age_exception
            | meets_disability_exception
            | meets_work_hours_exception
            | meets_parent_exception
            | receives_tanf
        )

        return is_higher_ed_student & ~meets_any_exception
