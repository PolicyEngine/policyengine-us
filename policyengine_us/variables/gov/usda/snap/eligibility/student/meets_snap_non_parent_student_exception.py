from policyengine_us.model_api import *


class meets_snap_non_parent_student_exception(Variable):
    value_type = bool
    entity = Person
    label = "Meets a SNAP student exception other than the parent exceptions"
    documentation = (
        "Whether a higher education student qualifies for SNAP through an "
        "exception that does not depend on caring for a child: age, "
        "disability, placement through an employment and training or work "
        "incentive program, work hours or work-study, or TANF receipt."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#e",
        "https://www.law.cornell.edu/cfr/text/7/273.5#b",
    )

    def formula(person, period, parameters):
        # Exception 1: Under 18 or age 50 or older
        age = person("age", period)
        p = parameters(period).gov.usda.snap.student
        # Cast to bool: single_amount bool brackets return int (0/1), which
        # would make a later ~ a bitwise negation instead of a logical one.
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

        # Exception 6: Receiving TANF benefits (part A of title IV)
        tanf = person("tanf_person", period)
        receives_tanf = (tanf > 0) | (
            add(person.spm_unit, period, ["receives_tanf"]) > 0
        )

        return (
            meets_age_exception
            | meets_disability_exception
            | meets_program_placement_exception
            | meets_work_hours_exception
            | receives_tanf
        )
