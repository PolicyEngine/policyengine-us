from policyengine_us.model_api import *


class dc_tanf_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Work requirement satisfied for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19b",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19g",
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_working = person("dc_tanf_is_working", period)
        work_requirement_exempt = person(
            "dc_tanf_work_requirement_exempt", period
        )
        meets_work_requirements = is_working | work_requirement_exempt
        return spm_unit.sum(~meets_work_requirements) == 0
