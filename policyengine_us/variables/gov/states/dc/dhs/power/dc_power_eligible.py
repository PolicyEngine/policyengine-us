from policyengine_us.model_api import *


class dc_power_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for DC Program on Work, Employment, and Responsibility (POWER)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72a",
    )
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head = person("is_tax_unit_head", period)
        work_exempted = person("dc_tanf_work_exempted", period)
        eligible_head = spm_unit.sum(is_head & work_exempted) == 1

        tanf_eligible = spm_unit("dc_tanf_eligible", period)
        no_tanf_ssi_ui_income = (
            add(spm_unit, period, ["ssi", "unemployment_compensation"]) == 0
        )

        return eligible_head & tanf_eligible & no_tanf_ssi_ui_income
