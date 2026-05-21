from policyengine_us.model_api import *


class ca_smc_general_assistance_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Mateo County General Assistance due to property"
    definition_period = YEAR
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/153295/download?inline=#page=2",
        "https://www.smcgov.org/media/156974/download?inline=",
        "https://sanmateocounty.legistar.com/View.ashx?GUID=25359405-C9EB-4566-AE97-D927CC455B02&ID=9802358&M=F#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.smc.general_assistance.property
        countable = spm_unit("ca_smc_general_assistance_countable_property", period)
        return countable < p.limit
