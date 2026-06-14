from policyengine_us.model_api import *


class ca_smc_general_assistance_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance payment standard"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/156974/download?inline=",
        "https://sanmateocounty.legistar.com/ViewReport.ashx?GID=659&GUID=LATEST&ID=94585&M=R&N=TextL5&Title=Board+Memo#page=1",
    )

    def formula(spm_unit, period, parameters):
        arrangement = spm_unit("ca_smc_general_assistance_living_arrangement", period)
        return parameters(period).gov.local.ca.smc.general_assistance.payment_standard[
            arrangement
        ]
