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
        work_exempted = person("dc_tanf_work_requirement_exempt", period)
        eligible_head = spm_unit.sum(is_head & work_exempted) == 1

        meets_basic_eligibility_requirements = spm_unit(
            "dc_tanf_basic_eligibility_requirements", period
        )
        no_tanf_ssi_ui_income = (
            add(
                spm_unit,
                period,
                ["dc_tanf", "ssi", "unemployment_compensation"],
            )
            == 0
        )

        return (
            eligible_head
            & meets_basic_eligibility_requirements
            & no_tanf_ssi_ui_income
        )
