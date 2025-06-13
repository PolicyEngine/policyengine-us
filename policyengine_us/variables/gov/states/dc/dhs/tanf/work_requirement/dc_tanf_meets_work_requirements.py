from policyengine_us.model_api import *


class dc_tanf_meets_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets work requirement for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19d"
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_working = person("dc_tanf_is_working_person", period)
        work_exempted = person("dc_tanf_work_exempted", period)
        ineligible_person = ~(is_working | work_exempted)
        return spm_unit.sum(ineligible_person) == 0
