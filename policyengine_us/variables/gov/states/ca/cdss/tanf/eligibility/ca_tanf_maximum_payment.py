from policyengine_us.model_api import *


class ca_tanf_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Maximum Aid Payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        ceiling = min_(unit_size, 10)
        region1 = spm_unit("ca_tanf_region1", period)
        exempt = spm_unit("ca_tanf_exempt", period)
        p = parameters(period).gov.states.ca.cdss.tanf.payment

        monthly = where(
            region1,
            where(
                exempt,
                p.region1.exempt[ceiling],
                p.region1.non_exempt[ceiling],
            ),
            where(
                exempt,
                p.region2.exempt[ceiling],
                p.region2.non_exempt[ceiling],
            ),
        )
        return monthly * MONTHS_IN_YEAR
