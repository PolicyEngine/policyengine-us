from policyengine_us.model_api import *


class is_snap_ineligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Is an ineligible student for SNAP"
    definition_period = YEAR
    defined_for = "is_snap_higher_ed_student"
    reference = "https://www.law.cornell.edu/uscode/text/7/2015#e"

    def formula(person, period, parameters):
        # Base rule: Students enrolled at least half-time in higher education
        # are ineligible (K-12 students are not affected by this rule).
        # This is guarded by defined_for = "is_snap_higher_ed_student".

        # Eight statutory exceptions that make students eligible:

        # Exception 1: Under 18 or age 50 or older
        age = person("age", period)
        p = parameters(period).gov.usda.snap.student
        # Cast to bool: single_amount bool brackets return int (0/1), which
        # would make the ~ below a bitwise negation instead of a logical one.
        meets_age_exception = p.age_threshold.calc(age).astype(bool)

        # Exception 2: Not physically or mentally fit (disabled)
        meets_disability_exception = person("is_disabled", period)

        # Exceptions 3 and 7: Placed in or enrolled in an institution of
        # higher education through a qualifying program — an employment and
        # training program (Exception 3: WIOA, SNAP E&T career/technical or
        # remedial coursework, the Trade Act, or a state or local program) or
        # a title IV work incentive / JOBS / TANF work program (Exception 7).
        meets_program_placement_exception = person(
            "is_snap_employment_training_or_work_incentive_student", period
        )

        # Exception 4: Employed at least 20 hours per week or work-study
        meets_work_hours_exception = person("meets_snap_work_exception", period)

        # Exception 5: Parent with responsibility for dependent child under 6,
        # or child 6-11 when adequate child care is not available
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        # (Exceptions 5 and 8 are implemented together)
        meets_parent_exception = person("meets_snap_parent_exception", period)

        # Exception 6: Receiving TANF benefits (part A of title IV)
        tanf = person("tanf_person", period)
        receives_tanf = (tanf > 0) | (
            add(person.spm_unit, period, ["receives_tanf"]) > 0
        )

        # Exception 7 is combined with Exception 3 above via
        # is_snap_employment_training_or_work_incentive_student.

        # A higher education student is INELIGIBLE if they do NOT meet ANY
        # of the eight exceptions
        return ~(
            meets_age_exception
            | meets_disability_exception
            | meets_program_placement_exception
            | meets_work_hours_exception
            | meets_parent_exception
            | receives_tanf
        )
