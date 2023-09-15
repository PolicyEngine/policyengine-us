from policyengine_us.model_api import *


class ca_tanf_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Maximum Aid Payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.monthly_payment
        unit_size = spm_unit("spm_unit_size", period)
        au_size = min_(unit_size, p.max_au_size)
        region1 = spm_unit("ca_tanf_region1", period)
        exempt = spm_unit("ca_tanf_exempt", period)

        max_monthly_payment = where(
            region1,
            where(
                exempt,
                p.region1.exempt[au_size],
                p.region1.non_exempt[au_size],
            ),
            where(
                exempt,
                p.region2.exempt[au_size],
                p.region2.non_exempt[au_size],
            ),
        )
        return max_monthly_payment * MONTHS_IN_YEAR
