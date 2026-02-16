from policyengine_us.model_api import *


class mt_tanf_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Work requirement satisfied for Montana Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.103",
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF705.1.pdf#page=1",
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_working = person("mt_tanf_is_working", period)
        is_disabled = person("is_disabled", period.this_year)
        work_requirement_exempt = (
            person("mt_tanf_eligible_child", period) | is_disabled
        )
        meets_work_requirements = is_working | work_requirement_exempt
        return spm_unit.sum(~meets_work_requirements) == 0
