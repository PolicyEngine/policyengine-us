from policyengine_us.model_api import *


class ca_smc_general_assistance_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Mateo County General Assistance payment standard"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = (
        "https://www.smcgov.org/media/156974/download?inline=#page=1",
        "https://sanmateocounty.legistar.com/ViewReport.ashx?GID=659&GUID=LATEST&ID=94585&M=R&N=TextL5&Title=Board+Memo#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.smc.general_assistance.payment_standard
        arrangement = spm_unit("ca_smc_general_assistance_living_arrangement", period)
        arrangements = arrangement.possible_values
        return select(
            [
                arrangement == arrangements.INDEPENDENT_LIVING,
                arrangement == arrangements.DRUG_ALCOHOL_TREATMENT_CENTER,
                arrangement == arrangements.NMOHC_WITHOUT_REFERRAL,
                arrangement == arrangements.NMOHC_WITH_REFERRAL,
            ],
            [
                p.independent_living,
                p.drug_alcohol_treatment_center,
                p.nmohc_without_referral,
                p.nmohc_with_referral,
            ],
            default=p.independent_living,
        )
