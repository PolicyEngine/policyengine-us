from policyengine_us.model_api import *


class nm_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "New Mexico CCAP family copayment"
    defined_for = StateCode.NM
    reference = (
        "https://www.nmececd.org/wp-content/uploads/2024/09/CCA-Co-payments-waived_rev1l.pdf#page=1",
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.ececd.ccap.copay
        # ECECD has waived all copayments since May 1, 2022, so families pay $0
        # while the waiver is in effect. The pre-2022 copayment formula
        # (8.15.2.13.B) is not modeled at the moment; in that era the
        # copayment is also treated as $0.
        if p.waived:
            return 0
        return 0
