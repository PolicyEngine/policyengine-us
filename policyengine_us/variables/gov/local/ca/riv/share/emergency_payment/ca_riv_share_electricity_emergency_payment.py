from policyengine_us.model_api import *


class ca_riv_share_electricity_emergency_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Riverside County Sharing Households Assist Riverside's Energy program (SHARE) electric emergency payment"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_riv_share_eligible"
    reference = "https://riversideca.gov/utilities/residents/assistance-programs/share-english"

    def formula(spm_unit, period, parameters):
        # This electric emergency payment only assign once per 12-month period
        p = parameters(period).gov.local.ca.riv.cap.share.payment
        is_urgent = spm_unit(
            "ca_riv_share_eligible_for_emergency_payment", period
        )
        return is_urgent * p.electricity_emergency
