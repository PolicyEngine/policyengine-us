from policyengine_us.model_api import *


class tx_tanf_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Work requirement satisfied for Texas Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/e-100-participation-texas-works-program",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-1405",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_working = person("tx_tanf_is_working", period)
        work_requirement_exempt = person(
            "tx_tanf_work_requirement_exempt", period
        )
        meets_work_requirements = is_working | work_requirement_exempt
        return spm_unit.sum(~meets_work_requirements) == 0
