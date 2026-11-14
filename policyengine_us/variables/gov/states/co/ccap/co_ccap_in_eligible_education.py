from policyengine_us.model_api import *


class co_ccap_in_eligible_education(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in education or training that counts as a Colorado Child Care Assistance Program activity"
    documentation = (
        "Enrollment in training, in a post-secondary program for a first "
        "bachelor's degree or less, or in basic education. Defaults to "
        "full-time school or college enrollment or part-time college "
        "enrollment. The model has no record of degree level, so set this to "
        "false for a graduate student or a second bachelor's degree."
    )
    definition_period = YEAR
    defined_for = StateCode.CO
    # PDF pages 39-40
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=39"

    def formula(person, period, parameters):
        # 3.111(G)(4)(a)(1) counts enrollment in training or a post-secondary
        # program for a first bachelor's degree or less, with no full-time
        # requirement, and 3.111(G)(4)(b) counts basic education.
        return person("is_full_time_student", period) | person(
            "is_part_time_college_student", period
        )
