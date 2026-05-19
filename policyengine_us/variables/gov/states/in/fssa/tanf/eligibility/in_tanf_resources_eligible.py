from policyengine_us.model_api import *


class in_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF resources eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-2",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-1-1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.resources.limit
        countable = spm_unit("in_tanf_countable_resources", period)
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        limit = where(
            is_enrolled,
            p.while_receiving.amount,
            p.at_application.amount,
        )
        return countable <= limit
