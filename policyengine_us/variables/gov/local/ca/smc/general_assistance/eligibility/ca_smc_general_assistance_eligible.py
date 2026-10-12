from policyengine_us.model_api import *


class ca_smc_general_assistance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Mateo County General Assistance"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/153295/download?inline=#page=1",
        "https://sanmateocounty.legistar.com/View.ashx?GUID=25359405-C9EB-4566-AE97-D927CC455B02&ID=9802358&M=F#page=2",
    )

    def formula(spm_unit, period, parameters):
        eligible_adult = (
            add(
                spm_unit,
                period,
                ["ca_smc_general_assistance_eligible_person"],
            )
            > 0
        )
        has_minor_child = add(spm_unit, period, ["is_child"]) > 0
        return (
            eligible_adult
            & ~has_minor_child
            & spm_unit("ca_smc_general_assistance_income_eligible", period)
            & spm_unit("ca_smc_general_assistance_property_eligible", period)
        )
