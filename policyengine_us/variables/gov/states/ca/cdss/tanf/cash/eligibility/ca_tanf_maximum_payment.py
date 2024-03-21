from policyengine_us.model_api import *


class ca_tanf_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Maximum Aid Payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://hhsaprogramguides.sandiegocounty.gov/CalWORKS/44-300/CalWORKs_Payment_Standards/G_CalWORKs_Payment_Standards.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.cash.monthly_payment
        unit_size = spm_unit("spm_unit_size", period)
        au_size = min_(unit_size, p.max_au_size)
        region1 = spm_unit.household("ca_tanf_region1", period)
        exempt = spm_unit("ca_tanf_exempt", period)
        # Indexing on exempt_name works, but not a similar string for region.
        # Use a where instead.
        exempt_name = where(exempt, "exempt", "non_exempt")
        return (
            where(
                region1,
                p.region1[exempt_name][au_size],
                p.region2[exempt_name][au_size],
            )
            * MONTHS_IN_YEAR
        )
