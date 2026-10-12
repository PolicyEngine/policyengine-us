from policyengine_us.model_api import *


STATE_TANF_WORK_REQUIREMENT_VARIABLES = [
    "dc_tanf_meets_work_requirements",
    "mt_tanf_meets_work_requirements",
]


class meets_tanf_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "TANF work requirement compliance"
    definition_period = MONTH
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        return add(spm_unit, period, STATE_TANF_WORK_REQUIREMENT_VARIABLES) > 0
