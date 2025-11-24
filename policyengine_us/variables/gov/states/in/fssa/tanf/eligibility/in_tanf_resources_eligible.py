from policyengine_us.model_api import *


class in_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Indiana TANF resource limit"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://casetext.com/regulation/indiana-administrative-code/title-470-division-of-family-resources/article-103-tanf-program",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.resources

        # Get countable resources
        countable_resources = spm_unit("in_tanf_countable_resources", period)

        # Check if already enrolled in TANF to determine which limit applies
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        # Select appropriate limit based on enrollment status
        # Use application limit for new applicants, higher limit for those already enrolled
        return countable_resources <= where(
            is_enrolled, p.limit_while_receiving, p.limit_at_application
        )
