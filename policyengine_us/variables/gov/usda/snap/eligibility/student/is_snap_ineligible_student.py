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

        # Eight statutory exceptions make students eligible. Exceptions 1-4,
        # 6 and 7 (age, disability, program placement, work hours or
        # work-study, TANF) do not depend on the household's children.
        meets_non_parent_exception = person(
            "meets_snap_non_parent_student_exception", period
        )

        # Exception 5: Parent with responsibility for dependent child under 6,
        # or child 6-11 when adequate child care is not available
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        # (Exceptions 5 and 8 are implemented together)
        meets_parent_exception = person("meets_snap_parent_exception", period)

        # A higher education student is INELIGIBLE if they do NOT meet ANY
        # of the eight exceptions
        return ~(meets_non_parent_exception | meets_parent_exception)
